"""
Integrated HR Agent combining LangChain/Gemini with HRMS structure
"""
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


@dataclass
class Teacher:
    id: int
    name: str
    phone: str
    department: Optional[str] = None
    available_leaves: int = 0
    pending_work: Optional[str] = None
    role_criticality: Optional[str] = None


@dataclass
class Leave:
    id: int
    teacher_id: int
    teacher_name: str
    start_date: date
    end_date: date
    days: int
    reason: str
    status: str = "pending"


@dataclass
class Substitution:
    id: int
    leave_id: int
    substitute_name: str
    status: str = "pending"


class IntegratedHRAgent:
    """HR Agent using LangChain + Gemini for intelligent leave decisions"""
    
    def __init__(self, excel_file: str = "employees.xlsx"):
        self.df = pd.read_excel(excel_file)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3
        )
        
        # Leave analysis prompt (AI provides insights, not decisions)
        self.leave_prompt = PromptTemplate(
            input_variables=["employee_data", "employee_name", "leave_days", "reason", "available_substitutes"],
            template="""
You are an AI HR Assistant analyzing a leave request. Provide insights to help the HOD make a decision.

Employee requesting leave:
Name: {employee_name}
Requested Leave Days: {leave_days}
Reason: {reason}

Employee record from HR database:
{employee_data}

Available substitutes for this period:
{available_substitutes}

Analyze and provide:
1. LEAVE BALANCE: Check if sufficient leaves are available
2. REASON VALIDITY: Assess if the reason is valid and urgent
3. ROLE IMPACT: Evaluate if the role is critical and can be substituted
4. WORKLOAD IMPACT: Check pending work and priority
5. SUBSTITUTE AVAILABILITY: Comment on available substitutes
6. RECOMMENDATION: Suggest approval or rejection with reasoning

Format your response clearly with these sections. Be objective and data-driven.
DO NOT make the final decision - only provide analysis and recommendation.
"""
        )
        
        self.chain = self.leave_prompt | self.llm | StrOutputParser()
        
        # In-memory storage (simulating database)
        self.leaves: List[Leave] = []
        self.substitutions: List[Substitution] = []
        self.leave_counter = 1
        self.sub_counter = 1
    
    def find_teacher_by_name(self, name: str) -> Optional[Dict]:
        """Find teacher in the Excel database"""
        teacher = self.df[self.df["name"].str.lower() == name.lower()]
        if teacher.empty:
            return None
        return teacher.to_dict(orient="records")[0]
    
    def suggest_substitutes(self, requesting_teacher: str, leave_days: int) -> List[str]:
        """Suggest available substitute teachers"""
        # Get all teachers except the one requesting leave
        available = self.df[self.df["name"].str.lower() != requesting_teacher.lower()]
        
        # Simple logic: suggest teachers with lower workload or same department
        substitutes = []
        for _, teacher in available.head(3).iterrows():
            substitutes.append(f"{teacher['name']} (Dept: {teacher.get('department', 'N/A')})")
        
        return substitutes
    
    def submit_leave_request(self, teacher_name: str, leave_days: int, reason: str) -> Dict:
        """Teacher submits a leave request"""
        teacher = self.find_teacher_by_name(teacher_name)
        
        if not teacher:
            return {"status": "error", "message": "Teacher not found in database"}
        
        # Create leave record
        leave = Leave(
            id=self.leave_counter,
            teacher_id=teacher.get("id", self.leave_counter),
            teacher_name=teacher_name,
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
            days=leave_days,
            reason=reason,
            status="pending"
        )
        self.leaves.append(leave)
        self.leave_counter += 1
        
        return {
            "status": "success",
            "message": f"Leave request #{leave.id} submitted. Awaiting HOD approval.",
            "leave_id": leave.id
        }
    
    def get_ai_analysis(self, leave_id: int) -> Dict:
        """Get AI analysis for a leave request (doesn't make decision)"""
        # Find the leave request
        leave = next((l for l in self.leaves if l.id == leave_id), None)
        if not leave:
            return {"status": "error", "message": "Leave request not found"}
        
        # Get teacher data
        teacher = self.find_teacher_by_name(leave.teacher_name)
        if not teacher:
            return {"status": "error", "message": "Teacher data not found"}
        
        # Get substitute suggestions
        substitutes = self.suggest_substitutes(leave.teacher_name, leave.days)
        substitute_str = "\n".join([f"- {s}" for s in substitutes]) if substitutes else "None available"
        
        # Get AI analysis
        response = self.chain.invoke({
            "employee_data": teacher,
            "employee_name": leave.teacher_name,
            "leave_days": leave.days,
            "reason": leave.reason,
            "available_substitutes": substitute_str
        })
        
        return {
            "status": "success",
            "leave_id": leave_id,
            "teacher_name": leave.teacher_name,
            "leave_days": leave.days,
            "reason": leave.reason,
            "ai_analysis": response,
            "substitutes": substitutes,
            "teacher_data": teacher
        }
    
    def approve_leave(self, leave_id: int) -> Dict:
        """HOD approves the leave request"""
        leave = next((l for l in self.leaves if l.id == leave_id), None)
        if not leave:
            return {"status": "error", "message": "Leave request not found"}
        
        leave.status = "approved"
        return {
            "status": "success",
            "message": f"Leave #{leave_id} approved for {leave.teacher_name}",
            "leave_id": leave_id
        }
    
    def reject_leave(self, leave_id: int, reason: str = "") -> Dict:
        """HOD rejects the leave request"""
        leave = next((l for l in self.leaves if l.id == leave_id), None)
        if not leave:
            return {"status": "error", "message": "Leave request not found"}
        
        leave.status = "rejected"
        return {
            "status": "success",
            "message": f"Leave #{leave_id} rejected for {leave.teacher_name}",
            "leave_id": leave_id,
            "rejection_reason": reason
        }
    
    def assign_substitute(self, leave_id: int, substitute_name: str) -> Dict:
        """Assign a substitute teacher to approved leave"""
        leave = next((l for l in self.leaves if l.id == leave_id), None)
        if not leave:
            return {"status": "error", "message": "Leave request not found"}
        
        if leave.status != "approved":
            return {"status": "error", "message": "Leave must be approved first"}
        
        # Check if substitute exists
        substitute = self.find_teacher_by_name(substitute_name)
        if not substitute:
            return {"status": "error", "message": "Substitute teacher not found"}
        
        # Create substitution record
        sub = Substitution(
            id=self.sub_counter,
            leave_id=leave_id,
            substitute_name=substitute_name,
            status="pending"
        )
        self.substitutions.append(sub)
        self.sub_counter += 1
        
        return {
            "status": "success",
            "message": f"Substitute {substitute_name} assigned to leave #{leave_id}",
            "substitution_id": sub.id
        }
    
    def confirm_substitution(self, substitution_id: int) -> Dict:
        """Substitute confirms acceptance"""
        sub = next((s for s in self.substitutions if s.id == substitution_id), None)
        if not sub:
            return {"status": "error", "message": "Substitution not found"}
        
        sub.status = "confirmed"
        return {
            "status": "success",
            "message": f"Substitution #{substitution_id} confirmed by {sub.substitute_name}"
        }
    
    def get_leave_status(self, leave_id: int) -> Dict:
        """Get current status of a leave request"""
        leave = next((l for l in self.leaves if l.id == leave_id), None)
        if not leave:
            return {"status": "error", "message": "Leave request not found"}
        
        # Get associated substitutions
        subs = [s for s in self.substitutions if s.leave_id == leave_id]
        
        return {
            "status": "success",
            "leave": {
                "id": leave.id,
                "teacher": leave.teacher_name,
                "days": leave.days,
                "reason": leave.reason,
                "status": leave.status
            },
            "substitutions": [
                {"id": s.id, "substitute": s.substitute_name, "status": s.status}
                for s in subs
            ]
        }
