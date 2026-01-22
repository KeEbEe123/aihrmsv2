"""
Unified WhatsApp Handler - Handles both employee and manager messages
Routes internally based on phone number authorization
"""
import os
import re
from datetime import datetime
from typing import Dict, Optional, Tuple
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv

from integrated_hr_agent import IntegratedHRAgent

load_dotenv()

app = Flask(__name__)

# Global instance to maintain session state across requests
unified_handler_instance = None

class UnifiedWhatsAppHandler:
    def __init__(self):
        self.hr_agent = IntegratedHRAgent()
        self.twilio_client = TwilioClient(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_from = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        
        # Session storage for conversation state
        if not hasattr(UnifiedWhatsAppHandler, '_user_sessions'):
            UnifiedWhatsAppHandler._user_sessions = {}
        if not hasattr(UnifiedWhatsAppHandler, '_manager_sessions'):
            UnifiedWhatsAppHandler._manager_sessions = {}
    
    @property
    def user_sessions(self):
        return UnifiedWhatsAppHandler._user_sessions
    
    @property
    def manager_sessions(self):
        return UnifiedWhatsAppHandler._manager_sessions
    
    def extract_phone_number(self, whatsapp_from: str) -> str:
        """Extract phone number from WhatsApp format"""
        return whatsapp_from.replace('whatsapp:', '')
    
    def is_manager(self, phone: str) -> bool:
        """Check if phone number belongs to a manager"""
        manager_phone = os.getenv('MANAGER_PHONE', '').replace('+', '').replace(' ', '')
        clean_phone = phone.replace('+', '').replace(' ', '')
        
        # Match last 10 digits
        return manager_phone[-10:] == clean_phone[-10:] if len(manager_phone) >= 10 else False
    
    def find_employee_by_phone(self, phone: str) -> Optional[Dict]:
        """Find employee by phone number in database"""
        # Clean phone number (remove country codes, spaces, etc.)
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        print(f"DEBUG: Looking for employee with phone: {phone}")
        print(f"DEBUG: Cleaned phone: {clean_phone}")
        print(f"DEBUG: Last 10 digits: {clean_phone[-10:]}")
        
        # Search in Excel database
        for _, employee in self.hr_agent.df.iterrows():
            emp_phone = str(employee.get('phone', ''))
            clean_emp_phone = re.sub(r'[^\d]', '', emp_phone)
            
            # Match last 10 digits (handles country codes)
            if len(clean_phone) >= 10 and len(clean_emp_phone) >= 10:
                if clean_phone[-10:] == clean_emp_phone[-10:]:
                    print(f"DEBUG: Found employee: {employee.get('name')} with phone {emp_phone}")
                    return employee.to_dict()
        
        print(f"DEBUG: No employee found for phone {phone}")
        return None
    
    def send_whatsapp_message(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp message via Twilio"""
        try:
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            self.twilio_client.messages.create(
                from_=self.twilio_from,
                to=to_phone,
                body=message
            )
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def route_message(self, phone: str, message: str) -> Tuple[str, str]:
        """Route message to appropriate handler based on phone number and message content"""
        
        # Check if message is a substitute response (Accept/Decline #ID)
        if self.is_substitute_response(message):
            return "substitute", self.handle_substitute_response(phone, message)
        
        # Check if user is a manager
        if self.is_manager(phone):
            # Check if message looks like a manager command
            if self.is_manager_command(message):
                return "manager", self.handle_manager_message(phone, message)
            else:
                # Manager might be applying for leave as an employee
                employee = self.find_employee_by_phone(phone)
                if employee:
                    return "employee", self.handle_employee_message(phone, message, employee)
                else:
                    return "manager", "👋 Hi! You can use manager commands or apply for leave as an employee.\n\nManager commands: 'List', 'Approve #1', 'Reject #1 reason'\nEmployee: 'I need 3 days leave for...'"
        else:
            # Regular employee
            employee = self.find_employee_by_phone(phone)
            if employee:
                return "employee", self.handle_employee_message(phone, message, employee)
            else:
                return "error", "❌ Sorry, I couldn't find your employee record. Please contact HR directly or ensure you're messaging from your registered phone number."
    
    def is_substitute_response(self, message: str) -> bool:
        """Check if message is a substitute response"""
        message_lower = message.lower().strip()
        
        # Check for accept/decline patterns with leave ID
        accept_patterns = [
            r'accept\s+#?\d+',
            r'yes\s+#?\d+',
            r'confirm\s+#?\d+',
            r'ok\s+#?\d+',
        ]
        
        decline_patterns = [
            r'decline\s+#?\d+',
            r'reject\s+#?\d+',
            r'no\s+#?\d+',
            r'cannot\s+#?\d+',
            r'can\'t\s+#?\d+',
        ]
        
        all_patterns = accept_patterns + decline_patterns
        
        return any(re.search(pattern, message_lower) for pattern in all_patterns)
    
    def is_manager_command(self, message: str) -> bool:
        """Check if message looks like a manager command"""
        message_lower = message.lower().strip()
        
        manager_keywords = [
            'approve', 'reject', 'deny', 'status', 'list', 'pending', 
            'assign', 'help', 'commands'
        ]
        
        # Check for manager command patterns
        has_leave_id = re.search(r'#?\d+', message)
        has_manager_keyword = any(keyword in message_lower for keyword in manager_keywords)
        
        return has_manager_keyword or (has_leave_id and len(message.split()) <= 5)
    
    def handle_substitute_response(self, phone: str, message: str) -> str:
        """Handle substitute accept/decline responses"""
        message_lower = message.lower().strip()
        
        # Extract leave ID
        leave_id_match = re.search(r'#?(\d+)', message)
        if not leave_id_match:
            return "❌ Please include the leave request ID. Example: 'Accept #1' or 'Decline #1'"
        
        leave_id = int(leave_id_match.group(1))
        
        # Find the substitute in database
        substitute = self.find_employee_by_phone(phone)
        if not substitute:
            return "❌ Sorry, I couldn't find your employee record."
        
        substitute_name = substitute['name']
        
        # Check if this person is actually assigned as substitute for this leave (case-insensitive comparison)
        substitution = next((s for s in self.hr_agent.substitutions 
                           if s.leave_id == leave_id 
                           and s.substitute_name.lower().strip() == substitute_name.lower().strip()), None)
        if not substitution:
            # Debug: Show what we're looking for
            all_subs_for_leave = [s for s in self.hr_agent.substitutions if s.leave_id == leave_id]
            if all_subs_for_leave:
                assigned_names = [s.substitute_name for s in all_subs_for_leave]
                return f"❌ You are not assigned as substitute for leave request #{leave_id}.\n\nAssigned substitutes: {', '.join(assigned_names)}\nYour name in system: {substitute_name}"
            else:
                return f"❌ No substitute has been assigned to leave request #{leave_id} yet."
        
        # Determine if accepting or declining
        if any(word in message_lower for word in ['accept', 'yes', 'confirm', 'ok']):
            return self.handle_substitute_accept(leave_id, substitute_name)
        elif any(word in message_lower for word in ['decline', 'reject', 'no', 'cannot', 'can\'t']):
            return self.handle_substitute_decline(leave_id, substitute_name)
        else:
            return "❌ Please clearly state 'Accept' or 'Decline'. Example: 'Accept #1' or 'Decline #1'"
    
    def handle_substitute_accept(self, leave_id: int, substitute_name: str) -> str:
        """Handle substitute accepting the assignment"""
        # Confirm the substitution
        result = self.hr_agent.confirm_substitution_by_leave_id(leave_id, substitute_name)
        if result['status'] != 'success':
            return f"❌ Error confirming substitution: {result['message']}"
        
        # Get leave details for notifications
        leave = next((l for l in self.hr_agent.leaves if l.id == leave_id), None)
        if not leave:
            return f"❌ Leave request #{leave_id} not found."
        
        # Get AI analysis for manager
        ai_analysis = self.hr_agent.get_ai_analysis(leave_id)
        
        # Notify the manager with substitute's acceptance
        manager_phone = os.getenv('MANAGER_PHONE')
        if manager_phone:
            manager_msg = f"""
🔔 New Leave Request #{leave_id} - Ready for Review

👤 Employee: {leave.teacher_name}
📅 Days: {leave.days} days
📝 Reason: {leave.reason}

👥 Substitute Status: ✅ ACCEPTED
• {substitute_name} has confirmed availability

🤖 AI Analysis Summary:
{ai_analysis.get('ai_analysis', 'Analysis not available')[:400]}...

📋 Action Required:
• "Approve #{leave_id}" - Approve this request
• "Reject #{leave_id} [reason]" - Reject with reason
• "Status #{leave_id}" - Check full details

Note: Employee will be notified after your decision.
            """.strip()
            
            self.send_whatsapp_message(f"whatsapp:{manager_phone}", manager_msg)
        
        # Notify the employee that substitute accepted
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
✅ Substitute Confirmed!

📋 Leave Request: #{leave_id}
👥 Substitute: {substitute_name} has accepted

⏳ Your request is now with the manager for final approval.
You'll be notified once a decision is made.
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        return f"""
✅ Thank you for accepting the substitute assignment!

📋 Leave Request: #{leave_id}
👤 Employee: {leave.teacher_name}
🗓️ Days: {leave.days} days

Your confirmation has been sent to the manager for final approval.
All parties will be notified of the decision.

Thank you for your support! 🙏
        """.strip()
    
    def handle_substitute_decline(self, leave_id: int, substitute_name: str) -> str:
        """Handle substitute declining the assignment"""
        # Update substitution status to declined
        substitution = next((s for s in self.hr_agent.substitutions if s.leave_id == leave_id and s.substitute_name.lower().strip() == substitute_name.lower().strip()), None)
        if substitution:
            substitution.status = "declined"
        
        # Get leave details
        leave = next((l for l in self.hr_agent.leaves if l.id == leave_id), None)
        if not leave:
            return f"❌ Leave request #{leave_id} not found."
        
        # Get AI analysis for manager
        ai_analysis = self.hr_agent.get_ai_analysis(leave_id)
        
        # Notify the manager that substitute declined
        manager_phone = os.getenv('MANAGER_PHONE')
        if manager_phone:
            # Get available substitutes for manager
            substitutes = ai_analysis.get('substitutes', []) if ai_analysis['status'] == 'success' else []
            substitute_list = "\n".join([f"• {sub}" for sub in substitutes]) if substitutes else "• No other substitutes available"
            
            manager_msg = f"""
🔔 Leave Request #{leave_id} - Substitute Declined

👤 Employee: {leave.teacher_name}
📅 Days: {leave.days} days
📝 Reason: {leave.reason}

👥 Substitute Status: ❌ DECLINED
• {substitute_name} is not available

🤖 AI Analysis Summary:
{ai_analysis.get('ai_analysis', 'Analysis not available')[:400]}...

💡 Available Alternatives:
{substitute_list}

📋 Action Required:
• "Assign [name] to #{leave_id}" - Assign another substitute
• "Reject #{leave_id} [reason]" - Reject the leave request
• "Status #{leave_id}" - Check full details

Note: Employee will be notified after your decision.
            """.strip()
            
            self.send_whatsapp_message(f"whatsapp:{manager_phone}", manager_msg)
        
        # Notify the employee that substitute declined
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
⚠️ Substitute Update

📋 Leave Request: #{leave_id}
👥 {substitute_name} is not available as substitute

⏳ Your request is with the manager who will:
• Assign another substitute, or
• Make a decision on your leave request

You'll be notified once a decision is made.
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        return f"""
✅ Thank you for your response!

📋 Leave Request: #{leave_id}
👤 Employee: {leave.teacher_name}

Your response has been forwarded to the manager.
They will assign another substitute or make a decision on the leave request.

Thank you for your prompt response! 🙏
        """.strip()
        """Check if message looks like a manager command"""
        message_lower = message.lower().strip()
        
        manager_keywords = [
            'approve', 'reject', 'deny', 'status', 'list', 'pending', 
            'assign', 'help', 'commands'
        ]
        
        # Check for manager command patterns
        has_leave_id = re.search(r'#?\d+', message)
        has_manager_keyword = any(keyword in message_lower for keyword in manager_keywords)
        
        return has_manager_keyword or (has_leave_id and len(message.split()) <= 5)
    
    # ==================== EMPLOYEE HANDLERS ====================
    
    def handle_employee_message(self, phone: str, message: str, employee: Dict) -> str:
        """Handle employee leave application flow"""
        session_key = phone
        
        # Special commands
        if message.lower().strip() in ['reset', 'restart', 'clear']:
            if session_key in self.user_sessions:
                del self.user_sessions[session_key]
            return f"Hi {employee['name']}! Session reset. How can I help you today?"
        
        # Initialize session if not exists
        if session_key not in self.user_sessions:
            self.user_sessions[session_key] = {
                'state': 'initial',
                'employee': employee,
                'leave_data': {}
            }
            print(f"DEBUG: Created new employee session for {phone}")
        
        session = self.user_sessions[session_key]
        state = session['state']
        
        print(f"DEBUG: Employee - Phone {phone}, State: {state}, Message: {message}")
        
        if state == 'initial':
            if self.parse_leave_intent(message):
                details = self.extract_leave_details(message)
                session['leave_data'].update(details)
                
                print(f"DEBUG: Extracted details: {details}")
                print(f"DEBUG: Session leave_data: {session['leave_data']}")
                
                missing_info = []
                if 'days' not in session['leave_data']:
                    missing_info.append('number of days')
                if 'reason' not in session['leave_data']:
                    missing_info.append('reason')
                
                print(f"DEBUG: Missing info: {missing_info}")
                
                if missing_info:
                    session['state'] = 'collecting_info'
                    return f"Hi {employee['name']}! I can help you apply for leave.\n\nI need:\n• {chr(10).join(missing_info)}\n\nPlease provide the missing details."
                else:
                    return self.confirm_leave_details(session)
            else:
                return f"Hi {employee['name']}! I can help you apply for leave. Please tell me:\n• How many days do you need?\n• What's the reason?\n\nExample: 'I need 3 days leave for family emergency'\n\n(Type 'reset' to start over)"
        
        elif state == 'collecting_info':
            new_details = self.extract_leave_details(message)
            session['leave_data'].update(new_details)
            
            print(f"DEBUG: New details from collecting_info: {new_details}")
            print(f"DEBUG: Updated session leave_data: {session['leave_data']}")
            
            if 'days' in session['leave_data'] and 'reason' in session['leave_data']:
                return self.confirm_leave_details(session)
            else:
                missing = []
                if 'days' not in session['leave_data']:
                    missing.append('number of days')
                if 'reason' not in session['leave_data']:
                    missing.append('reason')
                
                print(f"DEBUG: Still missing: {missing}")
                return f"I still need:\n• {chr(10).join(missing)}\n\nPlease provide the missing information."
        
        elif state == 'confirming':
            if message.lower().strip() in ['yes', 'y', 'confirm', 'ok', 'proceed']:
                return self.ask_for_substitute(session)
            elif message.lower().strip() in ['no', 'n', 'cancel']:
                del self.user_sessions[session_key]
                return "Leave application cancelled. Feel free to start again anytime!"
            else:
                return "Please reply with 'yes' to confirm or 'no' to cancel the leave application."
        
        elif state == 'selecting_substitute':
            return self.handle_substitute_selection(session, phone, message)
        
        return "I didn't understand. Please try again or type 'help' for assistance.\n\n(Type 'reset' to start over)"
    
    def parse_leave_intent(self, message: str) -> bool:
        """Check if message contains leave application intent using enhanced NLP"""
        message_lower = message.lower().strip()
        
        # Enhanced leave keywords and phrases
        leave_keywords = [
            # Direct leave requests
            'leave', 'apply for leave', 'need leave', 'want leave', 'request leave',
            'take leave', 'get leave', 'have leave', 'go on leave',
            
            # Time off variations
            'time off', 'day off', 'days off', 'week off', 'weeks off',
            'vacation', 'holiday', 'break', 'rest',
            
            # Absence indicators
            'absent', 'away', 'not available', 'unavailable', 'out of office',
            'won\'t be in', 'will be away', 'cannot come', 'can\'t come',
            
            # Specific leave types
            'sick leave', 'medical leave', 'casual leave', 'emergency leave',
            'personal leave', 'family leave', 'maternity leave', 'paternity leave',
            
            # Informal expressions
            'need to be away', 'have to go', 'going away', 'traveling',
            'not coming', 'skip work', 'miss work', 'off work'
        ]
        
        # Intent patterns with regex
        intent_patterns = [
            r'\bi\s+(need|want|would like|require|request)\s+.*(leave|time off|day off|vacation)',
            r'\bi\s+(will be|am going to be|gonna be)\s+.*(away|absent|unavailable|out)',
            r'\bi\s+(have to|need to|must)\s+.*(go|travel|be away|take time)',
            r'\bcan\s+i\s+(get|have|take)\s+.*(leave|time off|day off)',
            r'\bi\s+(won\'t|will not|cannot|can\'t)\s+be\s+(in|available|here)',
            r'\bapply\s+for\s+.*(leave|vacation|time off)',
            r'\brequest\s+.*(leave|vacation|time off)',
            r'\btake\s+.*(leave|vacation|time off|day off|week off)',
            r'\bneed\s+.*(leave|vacation|time off|day off|week off)',
            r'\bgoing\s+on\s+.*(leave|vacation|holiday)',
        ]
        
        # Check keywords
        keyword_match = any(keyword in message_lower for keyword in leave_keywords)
        
        # Check patterns
        pattern_match = any(re.search(pattern, message_lower) for pattern in intent_patterns)
        
        return keyword_match or pattern_match
    
    def extract_leave_details(self, message: str) -> Dict:
        """Extract leave details from message using enhanced NLP"""
        details = {}
        message_lower = message.lower().strip()
        
        # Enhanced day extraction patterns
        day_patterns = [
            # Direct numbers with days/weeks
            r'(\d+)\s*days?',
            r'(\d+)\s*weeks?',
            r'(\d+)\s*months?',
            
            # Written numbers
            r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*days?',
            r'(one|two|three|four)\s*weeks?',
            r'(a|an)\s*day',
            r'(a|an)\s*week',
            r'(a|an)\s*month',
            
            # Time expressions
            r'for\s+(\d+)\s*days?',
            r'for\s+(\d+)\s*weeks?',
            r'for\s+(a|an|one)\s*(day|week)',
            r'(\d+)\s*day\s*(leave|off|vacation)',
            r'(\d+)\s*week\s*(leave|off|vacation)',
            
            # Casual expressions
            r'couple\s+of\s+days',
            r'few\s+days',
            r'several\s+days',
        ]
        
        # Extract days
        for pattern in day_patterns:
            match = re.search(pattern, message_lower)
            if match:
                day_text = match.group(1)
                
                # Convert text numbers to digits
                text_to_num = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                    'a': 1, 'an': 1, 'couple': 2, 'few': 3, 'several': 4
                }
                
                if day_text.isdigit():
                    days = int(day_text)
                elif day_text in text_to_num:
                    days = text_to_num[day_text]
                else:
                    continue
                
                # Convert weeks/months to days
                if 'week' in match.group(0):
                    days *= 7
                elif 'month' in match.group(0):
                    days *= 30
                
                details['days'] = days
                break
        
        # Enhanced reason extraction patterns
        reason_patterns = [
            # Common prepositions
            r'for\s+(.+?)(?:\.|$|because|due to|since)',
            r'because\s+(.+?)(?:\.|$|for|due to)',
            r'due to\s+(.+?)(?:\.|$|because|for)',
            r'since\s+(.+?)(?:\.|$|because|for)',
            r'as\s+(.+?)(?:\.|$|because|for)',
            r'to\s+(.+?)(?:\.|$|because|for|due to)',  # Added "to" pattern
            
            # Reason indicators
            r'reason:?\s*(.+?)(?:\.|$)',
            r'purpose:?\s*(.+?)(?:\.|$)',
            
            # Medical/personal reasons (standalone)
            r'(sick|ill|unwell|not feeling well)',
            r'(doctor|hospital|medical|appointment)',
            r'(family|personal|emergency)',
            r'(vacation|holiday|travel|trip)',
            r'(wedding|marriage|funeral)',
            r'(pregnant|pregnancy|maternity|paternity)',
            r'(business|conference|meeting|training)',  # Added business reasons
            
            # Contextual extraction - more comprehensive
            r'i\s+(am|will be|have to|need to|must)\s+(.+?)(?:\.|$)',
            r'my\s+(.+?)(?:\.|$)',
            r'going\s+(.+?)(?:\.|$)',
            r'attending\s+(.+?)(?:\.|$)',  # Added attending pattern
            
            # Catch-all for "off" constructions
            r'off\s+(.+?)(?:\.|$)',
            r'leave\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in reason_patterns:
            match = re.search(pattern, message_lower)
            if match:
                reason = match.group(1).strip()
                
                # Clean up the reason
                reason = re.sub(r'^(to|for|because|due to|since|as)\s+', '', reason)
                reason = re.sub(r'\s+', ' ', reason)  # Remove extra spaces
                
                # Skip very short or generic reasons
                if len(reason) > 2 and reason not in ['it', 'this', 'that', 'some', 'the']:
                    details['reason'] = reason
                    break
        
        return details
    
    def confirm_leave_details(self, session: Dict) -> str:
        """Show leave details for confirmation"""
        leave_data = session['leave_data']
        employee = session['employee']
        
        confirmation_msg = f"""
📋 Leave Application Summary:

👤 Employee: {employee['name']}
📅 Days: {leave_data['days']} days
📝 Reason: {leave_data['reason']}
🏢 Department: {employee.get('department', 'N/A')}

Please reply 'YES' to confirm or 'NO' to cancel.
        """.strip()
        
        session['state'] = 'confirming'
        return confirmation_msg
    
    def ask_for_substitute(self, session: Dict) -> str:
        """Ask employee to suggest a substitute"""
        leave_data = session['leave_data']
        employee = session['employee']
        
        # Get available substitutes from HR system
        substitutes = self.hr_agent.suggest_substitutes(employee['name'], leave_data['days'])
        
        substitute_list = ""
        if substitutes:
            substitute_list = "\n\n🔄 Available colleagues:\n"
            for i, sub in enumerate(substitutes[:5], 1):
                substitute_list += f"{i}. {sub}\n"
            substitute_list += "\nYou can choose from the list above or suggest someone else."
        
        msg = f"""
✅ Leave details confirmed!

👤 Who would you like to suggest as your substitute during your absence?

This helps ensure your work is covered while you're away.{substitute_list}

Please reply with:
• The name of your preferred substitute
• "Skip" if you want to leave it to your manager
• "No substitute needed" if your role doesn't require coverage

Example: "Priya Sharma" or "Skip"
        """.strip()
        
        session['state'] = 'selecting_substitute'
        return msg
    
    def handle_substitute_selection(self, session: Dict, phone: str, message: str) -> str:
        """Handle substitute selection by employee"""
        message_lower = message.lower().strip()
        
        # Check for skip options
        if message_lower in ['skip', 'no substitute', 'no substitute needed', 'none', 'manager decides']:
            session['leave_data']['suggested_substitute'] = None
            session['leave_data']['substitute_note'] = "Employee prefers manager to decide"
            return self.submit_leave_request(session, phone)
        
        # Check for no substitute needed
        if message_lower in ['no substitute needed', 'not needed', 'no coverage needed']:
            session['leave_data']['suggested_substitute'] = None
            session['leave_data']['substitute_note'] = "No substitute coverage required"
            return self.submit_leave_request(session, phone)
        
        # Extract substitute name
        substitute_name = self.extract_substitute_name(message)
        
        if substitute_name:
            # Validate if substitute exists in database
            substitute = self.hr_agent.find_teacher_by_name(substitute_name)
            
            if substitute:
                session['leave_data']['suggested_substitute'] = substitute_name
                session['leave_data']['substitute_note'] = f"Employee suggested: {substitute_name}"
                
                # Submit leave request first to get leave ID
                result = self.submit_leave_request_with_substitute(session, phone, substitute_name, substitute)
                return result
            else:
                # Show available employees to help user
                available_employees = []
                for _, emp in self.hr_agent.df.iterrows():
                    if emp.get('name') and emp['name'].lower() != session['employee']['name'].lower():
                        available_employees.append(emp['name'])
                
                suggestion_list = ""
                if available_employees:
                    suggestion_list = f"\n\n💡 Available colleagues:\n"
                    for emp in available_employees[:5]:  # Show first 5
                        suggestion_list += f"• {emp}\n"
                    if len(available_employees) > 5:
                        suggestion_list += f"• ... and {len(available_employees) - 5} more"
                
                return f"""
❌ I couldn't find "{substitute_name}" in our employee database.{suggestion_list}

Please try again with:
• The exact name of a colleague from the list above
• "Skip" to let your manager decide  
• "No substitute needed" if no coverage required

Example: "Priya Sharma" or "Skip"
                """.strip()
        else:
            return """
❌ I didn't understand the substitute name.

Please reply with:
• The full name of your preferred substitute
• "Skip" if you want your manager to decide
• "No substitute needed" if no coverage required

Example: "Priya Sharma" or "Skip"
            """.strip()
    
    def submit_leave_request_with_substitute(self, session: Dict, phone: str, substitute_name: str, substitute: Dict) -> str:
        """Submit leave request and notify substitute immediately"""
        leave_data = session['leave_data']
        employee = session['employee']
        
        # Submit to HR system
        result = self.hr_agent.submit_leave_request(
            teacher_name=employee['name'],
            leave_days=leave_data['days'],
            reason=leave_data['reason'],
            suggested_substitute=substitute_name,
            substitute_note=leave_data.get('substitute_note')
        )
        
        if result['status'] == 'success':
            leave_id = result['leave_id']
            
            # Assign the substitute immediately
            assign_result = self.hr_agent.assign_substitute(leave_id, substitute_name)
            
            if assign_result['status'] == 'success':
                # Notify the substitute immediately
                substitute_phone = substitute.get('phone')
                if substitute_phone:
                    substitute_msg = f"""
🔔 Substitute Request from Colleague

Your colleague {employee['name']} has requested you as a substitute!

📋 Leave Details:
• Request ID: #{leave_id}
• Employee: {employee['name']}
• Days: {leave_data['days']} days
• Reason: {leave_data['reason']}

Please respond:
• "Accept #{leave_id}" - to confirm
• "Decline #{leave_id}" - if not available

⏰ Your response will be forwarded to the manager for final approval.
Thank you! 🙏
                    """.strip()
                    
                    self.send_whatsapp_message(f"whatsapp:+{substitute_phone}", substitute_msg)
            
            # Clear session
            if phone in self.user_sessions:
                del self.user_sessions[phone]
            
            return f"""
✅ Leave Request Submitted!

📋 Request ID: #{leave_id}
📅 Days: {leave_data['days']} days
📝 Reason: {leave_data['reason']}
👥 Suggested Substitute: {substitute_name}

🔔 {substitute_name} has been notified and asked to confirm availability.

⏳ Next Steps:
1. Substitute responds (Accept/Decline)
2. Manager reviews and makes final decision
3. You'll be notified of the outcome

Thank you! 🙏
            """.strip()
        else:
            return f"❌ Error submitting leave request: {result['message']}\n\nPlease try again or contact HR directly."
    
    def extract_substitute_name(self, message: str) -> str:
        """Extract substitute name from message"""
        message = message.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            'i suggest', 'i recommend', 'i prefer', 'i want', 'i choose',
            'suggest', 'recommend', 'prefer', 'choose', 'select',
            'my suggestion is', 'i think', 'maybe', 'how about'
        ]
        
        message_lower = message.lower()
        for prefix in prefixes_to_remove:
            if message_lower.startswith(prefix):
                message = message[len(prefix):].strip()
                break
        
        # Clean up the name
        message = re.sub(r'^(is|would be|could be|should be)\s+', '', message, flags=re.IGNORECASE)
        message = message.strip('.,!?')
        
        # Basic name validation (at least 1 word, reasonable length)
        words = message.split()
        if len(words) >= 1 and len(message) <= 50 and len(message) >= 2 and all(word.replace('-', '').replace("'", '').isalpha() for word in words):
            return message.title()  # Proper case
        
        return ""
    
    def submit_leave_request(self, session: Dict, phone: str) -> str:
        """Submit the leave request and notify manager"""
        leave_data = session['leave_data']
        employee = session['employee']
        
        # Submit to HR system
        result = self.hr_agent.submit_leave_request(
            teacher_name=employee['name'],
            leave_days=leave_data['days'],
            reason=leave_data['reason'],
            suggested_substitute=leave_data.get('suggested_substitute'),
            substitute_note=leave_data.get('substitute_note')
        )
        
        if result['status'] == 'success':
            leave_id = result['leave_id']
            
            # Get AI analysis
            ai_analysis = self.hr_agent.get_ai_analysis(leave_id)
            
            # Prepare substitute information for manager
            substitute_info = ""
            if leave_data.get('suggested_substitute'):
                substitute_info = f"\n\n👥 Employee's Substitute Suggestion:\n• {leave_data['suggested_substitute']}\n• Note: {leave_data.get('substitute_note', '')}"
            elif leave_data.get('substitute_note'):
                substitute_info = f"\n\n👥 Substitute Coverage:\n• {leave_data['substitute_note']}"
            
            # Notify manager
            manager_phone = os.getenv('MANAGER_PHONE')
            if manager_phone:
                manager_msg = f"""
🔔 New Leave Request #{leave_id}

👤 Employee: {employee['name']}
📞 Phone: {employee.get('phone', 'N/A')}
🏢 Department: {employee.get('department', 'N/A')}
📅 Days Requested: {leave_data['days']} days
📝 Reason: {leave_data['reason']}{substitute_info}

🤖 AI Analysis Summary:
{ai_analysis.get('ai_analysis', 'Analysis not available')[:500]}...

Commands:
• "Approve #{leave_id}" - Approve this request
• "Reject #{leave_id} [reason]" - Reject with reason
• "Status #{leave_id}" - Check status
                """.strip()
                
                self.send_whatsapp_message(f"whatsapp:{manager_phone}", manager_msg)
            
            # Clear session
            if phone in self.user_sessions:
                del self.user_sessions[phone]
            
            substitute_msg = ""
            if leave_data.get('suggested_substitute'):
                substitute_msg = f"\n👥 Suggested Substitute: {leave_data['suggested_substitute']}"
            
            return f"""
✅ Leave Request Submitted Successfully!

📋 Request ID: #{leave_id}
📅 Days: {leave_data['days']} days
📝 Reason: {leave_data['reason']}{substitute_msg}

Your manager has been notified and will review your request. You'll receive an update once it's processed.

Thank you! 🙏
            """.strip()
        
        else:
            return f"❌ Error submitting leave request: {result['message']}\n\nPlease try again or contact HR directly."
    
    # ==================== MANAGER HANDLERS ====================
    
    def handle_manager_message(self, phone: str, message: str) -> str:
        """Handle manager WhatsApp messages"""
        command = self.parse_manager_command(message)
        action = command.get('action')
        
        print(f"DEBUG: Manager command - Action: {action}, Command: {command}")
        
        if action == 'approve':
            return self.approve_leave(command['leave_id'])
        elif action == 'reject':
            return self.reject_leave(command['leave_id'], command.get('reason', ''))
        elif action == 'assign':
            return self.assign_substitute(command['leave_id'], command['substitute_name'])
        elif action == 'status':
            return self.get_leave_status(command['leave_id'])
        elif action == 'status_all':
            return self.get_all_leaves_status()
        elif action == 'list':
            return self.list_pending_leaves()
        elif action == 'help':
            return self.get_manager_help_message()
        else:
            return self.get_manager_help_message()
    
    def parse_manager_command(self, message: str) -> Dict:
        """Parse manager commands from WhatsApp message"""
        message_lower = message.lower().strip()
        
        # Check for approval commands
        if any(word in message_lower for word in ['approve', 'accept']):
            leave_id_match = re.search(r'#?(\d+)', message)
            if leave_id_match:
                return {'action': 'approve', 'leave_id': int(leave_id_match.group(1))}
        
        # Check for rejection commands
        elif any(word in message_lower for word in ['reject', 'deny']):
            leave_id_match = re.search(r'#?(\d+)', message)
            if leave_id_match:
                return {'action': 'reject', 'leave_id': int(leave_id_match.group(1)), 'reason': message}
        
        # Check for substitute assignment
        elif 'assign' in message_lower:
            assign_match = re.search(r'assign\s+(.+?)\s+to\s+#?(\d+)', message_lower)
            if assign_match:
                return {
                    'action': 'assign',
                    'substitute_name': assign_match.group(1).strip(),
                    'leave_id': int(assign_match.group(2))
                }
        
        # Check for status inquiry - differentiate between single leave and all leaves
        elif any(word in message_lower for word in ['status', 'check', 'info']):
            leave_id_match = re.search(r'#?(\d+)', message)
            if leave_id_match:
                return {'action': 'status', 'leave_id': int(leave_id_match.group(1))}
            else:
                # No ID provided, show all leaves status
                return {'action': 'status_all'}
        
        # Check for list pending leaves
        elif any(word in message_lower for word in ['list', 'pending', 'show']):
            return {'action': 'list'}
        
        # Check for help
        elif 'help' in message_lower or 'commands' in message_lower:
            return {'action': 'help'}
        
        return {'action': 'unknown'}
    
    def approve_leave(self, leave_id: int) -> str:
        """Approve a leave request (only after substitute is confirmed)"""
        ai_result = self.hr_agent.get_ai_analysis(leave_id)
        if ai_result['status'] != 'success':
            return f"❌ Error: {ai_result['message']}"
        
        result = self.hr_agent.approve_leave(leave_id)
        if result['status'] != 'success':
            return f"❌ Error: {result['message']}"
        
        # Get substitute info
        leave = next((l for l in self.hr_agent.leaves if l.id == leave_id), None)
        subs = [s for s in self.hr_agent.substitutions if s.leave_id == leave_id and s.status == 'confirmed']
        substitute_name = subs[0].substitute_name if subs else "None"
        
        # Notify the employee of final approval
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
✅ LEAVE APPROVED!

Your leave request #{leave_id} has been approved! 🎉

📅 Days: {ai_result['leave_days']} days
📝 Reason: {ai_result['reason']}
👥 Substitute: {substitute_name}

Your leave is now official. Enjoy your time off! 🌟

Have a great time!
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        # Notify the substitute of final approval
        if subs:
            substitute = self.hr_agent.find_teacher_by_name(substitute_name)
            if substitute and substitute.get('phone'):
                substitute_msg = f"""
✅ Leave Approved - Substitute Confirmed

The leave request you accepted has been approved!

📋 Leave Request: #{leave_id}
👤 Employee: {ai_result['teacher_name']}
📅 Days: {ai_result['leave_days']} days
👥 Your Role: Substitute Teacher

The leave is now official. Thank you for your support! 🙏
                """.strip()
                
                self.send_whatsapp_message(f"whatsapp:+{substitute.get('phone')}", substitute_msg)
        
        return f"""
✅ Leave #{leave_id} APPROVED!

👤 Employee: {ai_result['teacher_name']}
📅 Days: {ai_result['leave_days']} days
👥 Substitute: {substitute_name}

✅ Notifications sent to:
• Employee - Leave approved
• Substitute - Assignment confirmed

Status: APPROVED ✅
        """.strip()
    
    def notify_substitute(self, substitute_name: str, leave_id: int, employee_name: str) -> bool:
        """Notify substitute about assignment via WhatsApp"""
        # Find substitute in database
        substitute = self.hr_agent.find_teacher_by_name(substitute_name)
        
        if substitute and substitute.get('phone'):
            substitute_phone = f"whatsapp:+{substitute['phone']}"
            
            substitute_msg = f"""
🔔 Substitute Assignment Notification

You have been assigned as a substitute teacher!

📋 Details:
• Leave Request: #{leave_id}
• Employee: {employee_name}
• Your Role: Substitute Teacher

Please confirm your availability by replying:
• "Accept #{leave_id}" to confirm
• "Decline #{leave_id}" if not available

Thank you for your support! 🙏
            """.strip()
            
            return self.send_whatsapp_message(substitute_phone, substitute_msg)
        
        return False
    
    def reject_leave(self, leave_id: int, reason: str) -> str:
        """Reject a leave request"""
        ai_result = self.hr_agent.get_ai_analysis(leave_id)
        if ai_result['status'] != 'success':
            return f"❌ Error: {ai_result['message']}"
        
        # Get substitute info before rejecting
        subs = [s for s in self.hr_agent.substitutions if s.leave_id == leave_id]
        substitute_name = subs[0].substitute_name if subs else None
        substitute_status = subs[0].status if subs else None
        
        result = self.hr_agent.reject_leave(leave_id, reason)
        if result['status'] != 'success':
            return f"❌ Error rejecting leave: {result['message']}"
        
        # Notify the employee
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
❌ Leave Request Update

Your leave request #{leave_id} has been reviewed and cannot be approved at this time.

📅 Requested: {ai_result['leave_days']} days
📝 Reason: {ai_result['reason']}

💬 Manager's feedback: {reason}

Please contact your manager to discuss alternative arrangements or resubmit with different dates.
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        # Notify the substitute if they had accepted
        if substitute_name and substitute_status == 'confirmed':
            substitute = self.hr_agent.find_teacher_by_name(substitute_name)
            if substitute and substitute.get('phone'):
                substitute_msg = f"""
ℹ️ Leave Request Update

The leave request you accepted has been declined by management.

📋 Leave Request: #{leave_id}
👤 Employee: {ai_result['teacher_name']}
📅 Days: {ai_result['leave_days']} days

Your substitute assignment is no longer needed.
Thank you for your willingness to help! 🙏
                """.strip()
                
                self.send_whatsapp_message(f"whatsapp:+{substitute.get('phone')}", substitute_msg)
        
        notifications = "• Employee - Leave rejected"
        if substitute_name and substitute_status == 'confirmed':
            notifications += f"\n• Substitute ({substitute_name}) - Assignment cancelled"
        
        return f"""
❌ Leave #{leave_id} REJECTED

👤 Employee: {ai_result['teacher_name']}
📝 Rejection reason: {reason}

✅ Notifications sent to:
{notifications}

The employee can resubmit a new request if needed.
        """.strip()
        
        if substitute and substitute.get('phone'):
            substitute_phone = f"whatsapp:+{substitute['phone']}"
            
            substitute_msg = f"""
🔔 Substitute Assignment Notification

You have been assigned as a substitute teacher!

📋 Details:
• Leave Request: #{leave_id}
• Employee: {employee_name}
• Your Role: Substitute Teacher

Please confirm your availability by replying:
• "Accept #{leave_id}" to confirm
• "Decline #{leave_id}" if not available

Thank you for your support! 🙏
            """.strip()
            
            return self.send_whatsapp_message(substitute_phone, substitute_msg)
        
        return False
    
    def assign_substitute(self, leave_id: int, substitute_name: str) -> str:
        """Assign a substitute teacher to a leave request"""
        result = self.hr_agent.assign_substitute(leave_id, substitute_name)
        if result['status'] != 'success':
            return f"❌ Error: {result['message']}"
        
        # Get leave and employee details
        leave = next((l for l in self.hr_agent.leaves if l.id == leave_id), None)
        employee_name = leave.teacher_name if leave else "Unknown Employee"
        
        # Notify the substitute immediately
        notification_sent = self.notify_substitute(substitute_name, leave_id, employee_name)
        
        # Notify the employee that a substitute has been assigned
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
🔄 Leave Request Update

📋 Leave Request: #{leave_id}
👥 Substitute Assigned: {substitute_name}

⏳ Waiting for {substitute_name} to confirm availability.
You'll be notified once they respond and the manager makes a final decision.
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        notification_status = "✅ Notified via WhatsApp" if notification_sent else "⚠️ WhatsApp notification failed"
        
        return f"""
✅ Substitute Assigned Successfully!

👤 Substitute: {substitute_name}
📋 Leave ID: #{leave_id}
📱 Status: {notification_status}

⏳ PENDING: Waiting for substitute confirmation
• Substitute has been asked to Accept/Decline
• You'll be notified of their response
• Employee has been informed

Current Status: Substitute Assigned (Pending Confirmation)
        """.strip()
    
    def get_leave_status(self, leave_id: int) -> str:
        """Get status of a leave request"""
        result = self.hr_agent.get_leave_status(leave_id)
        if result['status'] != 'success':
            return f"❌ Error: {result['message']}"
        
        leave = result['leave']
        substitutions = result['substitutions']
        
        status_msg = f"""
📋 Leave Request #{leave['id']} Status

👤 Employee: {leave['teacher']}
📅 Days: {leave['days']} days
📝 Reason: {leave['reason']}
🔄 Status: {leave['status'].upper()}
        """
        
        if substitutions:
            status_msg += "\n\n🔄 Substitutions:"
            for sub in substitutions:
                status_msg += f"\n• {sub['substitute']} - {sub['status'].upper()}"
        
        return status_msg.strip()
    
    def get_all_leaves_status(self) -> str:
        """Get comprehensive status of all leave requests"""
        if not self.hr_agent.leaves:
            return "📋 No leave requests in the system yet."
        
        # Group leaves by status
        pending_leaves = []
        approved_leaves = []
        rejected_leaves = []
        in_progress_leaves = []
        
        for leave in self.hr_agent.leaves:
            if leave.status == 'approved':
                approved_leaves.append(leave)
            elif leave.status == 'rejected':
                rejected_leaves.append(leave)
            elif leave.status == 'pending':
                pending_leaves.append(leave)
            else:
                in_progress_leaves.append(leave)
        
        msg = "📊 ALL LEAVE REQUESTS STATUS\n"
        msg += "=" * 35 + "\n\n"
        
        # Pending leaves
        if pending_leaves:
            msg += "⏳ PENDING APPROVAL:\n"
            msg += "-" * 35 + "\n"
            for leave in pending_leaves:
                msg += f"#{leave.id} - {leave.teacher_name}\n"
                msg += f"📅 Days: {leave.days}\n"
                msg += f"📝 Reason: {leave.reason[:50]}{'...' if len(leave.reason) > 50 else ''}\n"
                msg += f"👥 Substitute: Not assigned\n"
                msg += f"Action: 'Approve #{leave.id}' or 'Reject #{leave.id}'\n\n"
        
        # In-progress leaves (substitute assigned/confirmed)
        if in_progress_leaves:
            msg += "🔄 IN PROGRESS:\n"
            msg += "-" * 35 + "\n"
            for leave in in_progress_leaves:
                # Get substitute info
                subs = [s for s in self.hr_agent.substitutions if s.leave_id == leave.id]
                sub_info = "None"
                if subs:
                    sub_info = f"{subs[0].substitute_name} ({subs[0].status})"
                
                status_emoji = "⏳" if leave.status == "substitute_assigned" else "✅"
                msg += f"#{leave.id} - {leave.teacher_name}\n"
                msg += f"📅 Days: {leave.days}\n"
                msg += f"📝 Reason: {leave.reason[:50]}{'...' if len(leave.reason) > 50 else ''}\n"
                msg += f"👥 Substitute: {sub_info}\n"
                msg += f"🔄 Status: {leave.status.replace('_', ' ').title()}\n"
                
                if leave.status == "substitute_confirmed":
                    msg += f"Action: 'Approve #{leave.id}' to finalize\n"
                elif leave.status == "substitute_assigned":
                    msg += f"Waiting for substitute confirmation\n"
                msg += "\n"
        
        # Approved leaves
        if approved_leaves:
            msg += "✅ APPROVED:\n"
            msg += "-" * 35 + "\n"
            for leave in approved_leaves:
                # Get substitute info
                subs = [s for s in self.hr_agent.substitutions if s.leave_id == leave.id]
                sub_info = "None"
                if subs:
                    sub_info = subs[0].substitute_name
                
                msg += f"#{leave.id} - {leave.teacher_name}\n"
                msg += f"📅 Days: {leave.days}\n"
                msg += f"📝 Reason: {leave.reason[:50]}{'...' if len(leave.reason) > 50 else ''}\n"
                msg += f"👥 Substitute: {sub_info}\n\n"
        
        # Rejected leaves
        if rejected_leaves:
            msg += "❌ REJECTED:\n"
            msg += "-" * 35 + "\n"
            for leave in rejected_leaves:
                msg += f"#{leave.id} - {leave.teacher_name}\n"
                msg += f"📅 Days: {leave.days}\n"
                msg += f"📝 Reason: {leave.reason[:50]}{'...' if len(leave.reason) > 50 else ''}\n\n"
        
        # Summary
        msg += "=" * 35 + "\n"
        msg += f"📊 SUMMARY:\n"
        msg += f"Total: {len(self.hr_agent.leaves)} | "
        msg += f"Pending: {len(pending_leaves)} | "
        msg += f"In Progress: {len(in_progress_leaves)} | "
        msg += f"Approved: {len(approved_leaves)} | "
        msg += f"Rejected: {len(rejected_leaves)}"
        
        return msg.strip()
    
    def list_pending_leaves(self) -> str:
        """List all pending leave requests"""
        pending_leaves = [l for l in self.hr_agent.leaves if l.status == 'pending']
        
        if not pending_leaves:
            return "📋 No pending leave requests at the moment."
        
        msg = "📋 Pending Leave Requests:\n\n"
        for leave in pending_leaves:
            msg += f"#{leave.id} - {leave.teacher_name}\n"
            msg += f"📅 {leave.days} days\n"
            msg += f"📝 {leave.reason}\n"
            msg += f"Commands: 'Approve #{leave.id}' or 'Reject #{leave.id} [reason]'\n\n"
        
        return msg.strip()
    
    def get_employee_phone_by_leave_id(self, leave_id: int) -> Optional[str]:
        """Get employee phone number by leave ID"""
        leave = next((l for l in self.hr_agent.leaves if l.id == leave_id), None)
        if not leave:
            return None
        
        employee = self.hr_agent.find_teacher_by_name(leave.teacher_name)
        if employee:
            phone = str(employee.get('phone', ''))
            return f"whatsapp:+{phone}" if phone else None
        
        return None
    
    def get_manager_help_message(self) -> str:
        """Get help message for managers"""
        return """
🤖 Manager Commands Help

📋 Leave Management:
• "List" - Show pending requests only
• "Status" - Show ALL leaves (pending, approved, rejected)
• "Status #123" - Check specific leave details
• "Approve #123" - Approve leave request
• "Reject #123 [reason]" - Reject with reason

🔄 Substitute Assignment:
• "Assign [name] to #123" - Assign substitute

📞 Examples:
• "Status" - See all leaves with full details
• "List" - See only pending leaves
• "Status #1" - Check leave #1 details
• "Approve #1"
• "Reject #1 Not enough coverage"
• "Assign Priya Sharma to #1"

You can also apply for leave as an employee by saying:
"I need 3 days leave for..."
        """.strip()

# Flask webhook endpoint
@app.route('/webhook', methods=['POST', 'GET'])
def unified_webhook():
    """Handle all incoming WhatsApp messages - routes internally"""
    global unified_handler_instance
    
    # Use singleton pattern to maintain session state
    if unified_handler_instance is None:
        unified_handler_instance = UnifiedWhatsAppHandler()
    
    handler = unified_handler_instance
    
    print(f"Unified webhook called with method: {request.method}")
    print(f"Request data: {request.values}")
    
    if request.method == 'GET':
        return "Unified WhatsApp webhook is working!", 200
    
    try:
        # Get message details
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        print(f"Incoming message: '{incoming_msg}' from {from_number}")
        
        # Extract phone number
        phone = handler.extract_phone_number(from_number)
        print(f"Extracted phone: {phone}")
        
        # Route message to appropriate handler
        message_type, response_msg = handler.route_message(phone, incoming_msg)
        print(f"Message type: {message_type}")
        print(f"Response: {response_msg}")
        
        # Create response
        resp = MessagingResponse()
        resp.message(response_msg)
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in unified webhook: {e}")
        import traceback
        traceback.print_exc()
        resp = MessagingResponse()
        resp.message("❌ Sorry, there was an error processing your request. Please try again.")
        return Response(str(resp), mimetype='text/xml')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "unified-whatsapp-handler", "timestamp": datetime.now().isoformat()}

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    print("🚀 Starting Unified WhatsApp HR Handler...")
    print(f"📱 Webhook URL: http://0.0.0.0:{port}/webhook")
    print("🌐 Make sure to expose this via ngrok for Twilio (local) or use Render URL (production)")
    print("👥 Handles both employee and manager messages automatically")
    app.run(debug=debug, host='0.0.0.0', port=port)