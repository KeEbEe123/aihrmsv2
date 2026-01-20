import pandas as pd
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Load employee data
df = pd.read_excel("employees.xlsx")

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# Prompt Template
prompt = PromptTemplate(
    input_variables=["employee_data", "employee_name", "leave_days", "reason"],
    template="""
You are an AI HR assistant.

Employee requesting leave:
Name: {employee_name}
Requested Leave Days: {leave_days}
Reason: {reason}

Employee record from HR database:
{employee_data}

Rules:
- Leave can be approved if sufficient leaves are available.
- If the role is critical and cannot be substituted, be strict.
- If pending work is high priority, suggest alternatives.
- Respond professionally like an HR manager.

Give a clear decision:
- Approved
- Rejected
- Conditionally Approved

Also explain WHY.
"""
)

chain = prompt | llm | StrOutputParser()

def process_leave_request(employee_name, leave_days, reason):
    employee = df[df["name"].str.lower() == employee_name.lower()]

    if employee.empty:
        return "Employee not found."

    employee_data = employee.to_dict(orient="records")[0]

    response = chain.invoke({
        "employee_data": employee_data,
        "employee_name": employee_name,
        "leave_days": leave_days,
        "reason": reason
    })

    return response
