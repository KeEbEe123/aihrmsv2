# Unified WhatsApp HR System Setup Guide

**Single webhook handles both employee and manager messages automatically!**

## 🎯 How It Works

### **Smart Message Routing:**
- **Same WhatsApp number** for both employees and managers
- **Automatic detection** of user type and message intent
- **Internal routing** to appropriate handlers
- **No separate webhooks needed**

### **User Detection:**
1. **Manager Detection**: Phone number matches `MANAGER_PHONE` in `.env`
2. **Message Analysis**: Checks for manager commands vs. leave requests
3. **Dual Role Support**: Managers can also apply for leave as employees

### **Message Flow:**
```
WhatsApp Message → Single Webhook → Smart Router → Employee/Manager Handler → Response
```

## 🚀 Quick Setup (2 Minutes)

### **Step 1: Start the System**
```bash
python unified_whatsapp_handler.py
# OR
python start_unified_system.py
```

### **Step 2: Expose via Ngrok**
```bash
ngrok http 5000
```

### **Step 3: Configure Twilio**
- **Single webhook URL**: `https://your-ngrok.ngrok-free.dev/webhook`
- **That's it!** No multiple URLs needed

## 📱 Message Examples

### **Employee Messages:**
```
"I need 3 days leave for family emergency"
"Apply for 2 days sick leave"
"Want leave for 5 days due to medical reasons"
```

### **Manager Messages:**
```
"List"                          → Show pending requests
"Approve #1"                    → Approve leave request #1
"Reject #1 Not enough coverage" → Reject with reason
"Status #1"                     → Check leave status
"Assign Priya Sharma to #1"     → Assign substitute
```

### **Manager as Employee:**
```
"I need 1 day leave for doctor appointment"
→ Manager can also apply for leave like any employee
```

## 🔄 Complete Workflow Example

### **1. Employee Applies**
```
Employee: "I need 3 days leave because my wife is pregnant"
Bot: "📋 Leave Application Summary: [details] Reply YES to confirm"
Employee: "YES"
Bot: "✅ Leave Request #1 submitted! Manager notified."
```

### **2. Manager Gets Auto-Notification**
```
Manager receives: "🔔 New Leave Request #1
                  👤 Employee: Rahul
                  📅 Days: 3 days
                  📝 Reason: wife is pregnant
                  🤖 AI Analysis: [Gemini insights]
                  Commands: 'Approve #1' or 'Reject #1 reason'"
```

### **3. Manager Approves**
```
Manager: "Approve #1"
Bot: "✅ Leave #1 APPROVED! Employee notified.
     Available substitutes: • Priya Sharma • Amit Singh"
```

### **4. Employee Gets Auto-Notification**
```
Employee receives: "✅ Great News! Your leave request #1 has been APPROVED!
                   📅 Days: 3 days
                   Enjoy your time off! 🌟"
```

### **5. Manager Assigns Substitute**
```
Manager: "Assign Priya Sharma to #1"
Bot: "✅ Substitute assigned! Priya has been notified."
```

## 🧠 Smart Routing Logic

### **How It Determines User Type:**

1. **Phone Number Check**: 
   - If phone matches `MANAGER_PHONE` → Potential manager
   - Otherwise → Employee

2. **Message Analysis**:
   - Manager commands: "Approve", "Reject", "List", "Status", "Assign"
   - Leave requests: "I need", "apply for leave", "want leave"

3. **Context-Aware Routing**:
   - Manager saying "List" → Manager handler
   - Manager saying "I need 2 days leave" → Employee handler
   - Employee saying "Approve #1" → Error (not authorized)

### **Authorization:**
- **Managers**: Can use both manager commands AND apply for leave
- **Employees**: Can only apply for leave, cannot approve/reject
- **Unknown numbers**: Get "employee not found" message

## 🔧 Configuration

### **Environment Variables:**
```bash
# Single webhook configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Manager authorization
MANAGER_PHONE=+918106778477

# AI integration
GOOGLE_API_KEY=your_google_api_key
```

### **Employee Database (employees.xlsx):**
```
name        | phone        | department   | available_leaves
Rahul       | 918106778477 | Engineering  | 5
Priya       | 918106778478 | Engineering  | 8
```

## 🧪 Testing

### **Test Script:**
```bash
python test_whatsapp_integration.py
```

### **Manual Testing:**
1. **Employee flow**: Send leave request from employee number
2. **Manager flow**: Send "List" from manager number
3. **Dual role**: Send leave request from manager number

### **Test Commands:**
```bash
# Employee messages
emp +918106778477 "I need 3 days leave for emergency"

# Manager messages  
mgr +918106778477 "List"
mgr +918106778477 "Approve #1"
```

## 🎛️ Advanced Features

### **1. Intelligent Command Detection**
- Recognizes manager commands even with typos
- Handles various formats: "approve 1", "Approve #1", "APPROVE 1"

### **2. Context Preservation**
- Maintains conversation state across messages
- Remembers partial leave applications
- Session management for complex flows

### **3. Error Handling**
- Graceful fallbacks for unrecognized messages
- Clear error messages for unauthorized actions
- Automatic session recovery

### **4. Dual Role Support**
- Managers can seamlessly switch between roles
- No confusion between manager commands and leave requests
- Proper authorization checks

## 🔍 Troubleshooting

### **Common Issues:**

**1. Manager commands not working:**
- Check `MANAGER_PHONE` in `.env` matches exactly
- Ensure phone number format is consistent
- Try "help" command to verify manager status

**2. Employee not found:**
- Verify phone number in `employees.xlsx`
- Check phone number format (with/without country code)
- Ensure last 10 digits match

**3. Messages not routing correctly:**
- Check Flask console logs for routing decisions
- Verify message format and keywords
- Test with simple commands first

### **Debug Mode:**
```bash
FLASK_DEBUG=1 python unified_whatsapp_handler.py
```

## 🚀 Production Deployment

### **Single App Deployment:**
```bash
# Deploy to Heroku
heroku create hr-whatsapp-unified
git add .
git commit -m "Unified WhatsApp HR System"
git push heroku main

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set MANAGER_PHONE=+918106778477
```

### **Twilio Configuration:**
- **Webhook URL**: `https://hr-whatsapp-unified.herokuapp.com/webhook`
- **Method**: POST
- **That's it!** Single webhook handles everything

## 🎯 Key Benefits

✅ **Simplified Setup** - Single webhook, single deployment  
✅ **Smart Routing** - Automatic user type detection  
✅ **Dual Role Support** - Managers can be employees too  
✅ **No URL Management** - One webhook URL for everything  
✅ **Easy Maintenance** - Single codebase to manage  
✅ **Cost Effective** - One server, one domain  
✅ **Scalable** - Easy to add new user types  

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 UNIFIED WHATSAPP HANDLER                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📱 Single WhatsApp Number                                   │
│  https://your-app.com/webhook                                │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │  Smart Router   │                                         │
│  │  • Phone Check  │                                         │
│  │  • Message Type │                                         │
│  │  • Intent Analysis                                        │
│  └────────┬────────┘                                         │
│           │                                                   │
│     ┌─────▼─────┐                                            │
│     │ Manager?  │                                            │
│     └─────┬─────┘                                            │
│           │                                                   │
│    ┌──────▼──────┐                                           │
│    │ Command or  │                                           │
│    │ Leave Req?  │                                           │
│    └──────┬──────┘                                           │
│           │                                                   │
│  ┌────────▼────────┐         ┌─────────────────┐            │
│  │ Manager Handler │         │ Employee Handler │            │
│  │ • Approve/Reject│         │ • Leave Requests │            │
│  │ • List Pending  │         │ • Conversation   │            │
│  │ • Assign Subs   │         │ • Confirmations  │            │
│  └─────────────────┘         └─────────────────┘            │
│           │                           │                       │
│           ▼                           ▼                       │
│  ┌─────────────────────────────────────────────┐            │
│  │           AI AGENT INTEGRATION               │            │
│  │  • LangChain + Google Gemini                │            │
│  │  • Employee Database Lookup                 │            │
│  │  • Leave Policy Analysis                    │            │
│  │  • Substitute Suggestions                   │            │
│  └─────────────────────────────────────────────┘            │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────────────────────────────────┐            │
│  │         AUTOMATIC NOTIFICATIONS              │            │
│  │  • Manager → Employee (Approval/Rejection)   │            │
│  │  • Employee → Manager (New Requests)         │            │
│  │  • System → Substitutes (Assignments)        │            │
│  └─────────────────────────────────────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

**Ready to revolutionize your HR system with a single, intelligent WhatsApp webhook? Start with the quick setup above! 🚀**