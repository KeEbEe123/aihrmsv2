# AI-Powered HRMS with LangChain + Google Gemini

An intelligent leave management system that combines LangChain with Google Gemini LLM for smart HR decisions.

## Features

✅ **AI-Powered Leave Approval** - Uses Google Gemini to analyze leave requests intelligently  
✅ **Substitute Teacher Management** - Suggests and assigns substitute teachers  
✅ **Complete Workflow** - Teacher request → HOD approval → Substitute assignment → Confirmation  
✅ **Excel-Based Database** - Simple employee data management  
✅ **Interactive Demo** - Two demo modes for testing

## Architecture

This integrates:
- **Your LangChain POC** (hr_agent.py) - Gemini LLM with intelligent prompting
- **ai-powered-hrms structure** - Complete workflow management (leaves, substitutions, notifications)

### Key Components

- `integrated_hr_agent.py` - Main agent combining LangChain + HRMS logic
- `demo.py` - Interactive demo with two modes
- `employees.xlsx` - Employee database
- `.env` - Google API key configuration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Google API key in `.env`:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Ensure `employees.xlsx` has the required columns:
   - name
   - department
   - available_leaves
   - pending_work
   - role_criticality

## Usage

Run the demo:
```bash
python demo.py
```

### Demo Modes

**Mode 1: Complete Workflow Demo (Guided)**
- Step-by-step walkthrough of the entire leave process
- Default values provided for quick testing
- Shows: Request → AI Analysis → Substitute Assignment → Confirmation

**Mode 2: Interactive Mode**
- Manual control over each action
- Test multiple scenarios
- Options:
  1. Submit leave request
  2. Process leave with AI
  3. Assign substitute
  4. Confirm substitution
  5. Check leave status

## Workflow Example

```
Teacher (Ravi Kumar) → Submits 3-day leave request
                     ↓
HOD → Reviews with AI assistance
    ↓
AI Agent → Analyzes: available leaves, role criticality, pending work
         → Decision: APPROVED/REJECTED/CONDITIONAL
         → Suggests substitutes
                     ↓
HOD → Assigns substitute (Priya Sharma)
                     ↓
Substitute → Confirms acceptance
                     ↓
System → Updates all statuses
```

## AI Decision Factors

The Gemini LLM considers:
- Available leave balance
- Role criticality (can it be substituted?)
- Pending high-priority work
- Available substitute teachers
- Department and subject expertise

## Next Steps

To integrate with the full ai-powered-hrms system:
1. Replace in-memory storage with Supabase database
2. Add Twilio WhatsApp notifications
3. Implement FastAPI endpoints
4. Add authentication and authorization
5. Deploy with Docker

## Files

- `integrated_hr_agent.py` - Core agent logic
- `demo.py` - Demo application
- `hr_agent.py` - Original LangChain POC
- `employees.xlsx` - Employee data
- `.env` - Configuration
- `ai-powered-hrms/` - Full HRMS system (reference)
