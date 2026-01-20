# Manager WhatsApp Setup Guide

Complete guide for setting up the manager approval system via WhatsApp.

## 🎯 How It Works

### **Employee Flow:**
1. Employee sends: `"I need 3 days leave for family emergency"`
2. Bot collects details and submits request
3. **Manager gets notified automatically** with AI analysis

### **Manager Flow:**
1. Manager receives notification with leave details + AI insights
2. Manager replies: `"Approve #1"` or `"Reject #1 reason"`
3. **Employee gets notified automatically** of decision
4. Manager can assign substitutes: `"Assign Priya Sharma to #1"`

## 🚀 Setup Options

### **Option 1: Same WhatsApp Number (Testing)**
Use one webhook for both employees and managers - simpler for testing.

### **Option 2: Separate WhatsApp Numbers (Production)**
Separate webhooks for employees and managers - more secure and scalable.

---

## 📱 Option 2 Setup (Recommended)

### **Step 1: Start Both Webhooks**

**Terminal 1:**
```bash
python whatsapp_hr_agent.py
# Employee webhook runs on port 5000
```

**Terminal 2:**
```bash
python manager_whatsapp_handler.py
# Manager webhook runs on port 5001
```

**Or use the combined starter:**
```bash
python start_whatsapp_system.py
# Starts both webhooks automatically
```

### **Step 2: Expose Both Ports via Ngrok**

**Terminal 3:**
```bash
ngrok http 5000
# Copy the HTTPS URL for employee webhook
```

**Terminal 4:**
```bash
ngrok http 5001
# Copy the HTTPS URL for manager webhook
```

### **Step 3: Configure Twilio Webhooks**

**For Employee WhatsApp:**
- Go to Twilio Console → WhatsApp Sandbox
- Set webhook URL: `https://your-employee-ngrok.ngrok-free.dev/webhook`

**For Manager WhatsApp:**
- Create second Twilio WhatsApp number OR use same number with different webhook
- Set webhook URL: `https://your-manager-ngrok.ngrok-free.dev/manager-webhook`

## 🎮 Manager Commands

### **Leave Management:**
```
List                    → Show all pending requests
Approve #1              → Approve leave request #1
Reject #1 [reason]      → Reject with reason
Status #1               → Check leave status
```

### **Substitute Management:**
```
Assign Priya Sharma to #1    → Assign substitute to leave #1
```

### **Examples:**
```
Manager: "List"
Bot: "📋 Pending Leave Requests:
     #1 - Rahul
     📅 3 days
     📝 family emergency"

Manager: "Approve #1"
Bot: "✅ Leave #1 APPROVED! Employee notified.
     Available substitutes: • Priya Sharma • Amit Singh"

Manager: "Assign Priya Sharma to #1"
Bot: "✅ Substitute assigned! Priya has been notified."
```

## 🔄 Complete Workflow Example

### **1. Employee Applies for Leave**
```
Employee: "I need 3 days leave because my wife is pregnant"
Bot: "Leave Application Summary: [details]"
Employee: "YES"
Bot: "✅ Leave Request #1 submitted!"
```

### **2. Manager Gets Notification**
```
Manager receives: "🔔 New Leave Request #1
                  👤 Employee: Rahul
                  📅 Days: 3 days
                  📝 Reason: wife is pregnant
                  
                  🤖 AI Analysis:
                  LEAVE BALANCE: ✅ Has 5 days available
                  REASON VALIDITY: ✅ Valid family emergency
                  ROLE IMPACT: ⚠️ Backend Dev - Medium criticality
                  WORKLOAD: ⚠️ Has pending API bug fixes
                  SUBSTITUTES: ✅ 3 available developers
                  RECOMMENDATION: APPROVE with substitute assignment"
```

### **3. Manager Approves**
```
Manager: "Approve #1"
Bot: "✅ Leave #1 APPROVED! Employee notified.
     Available substitutes:
     • Priya Sharma (Dept: Engineering)
     • Amit Singh (Dept: Engineering)"
```

### **4. Employee Gets Approval**
```
Employee receives: "✅ Great News! Your leave request #1 has been APPROVED!
                   📅 Days: 3 days
                   📝 Reason: wife is pregnant
                   Enjoy your time off! 🌟"
```

### **5. Manager Assigns Substitute**
```
Manager: "Assign Priya Sharma to #1"
Bot: "✅ Substitute assigned! Priya has been notified."
```

### **6. Substitute Gets Notification**
```
Priya receives: "🔔 Substitute Assignment
                You have been assigned for leave request #1.
                Reply 'Accept #1' to confirm or 'Decline #1' if not available."
```

## 🔐 Security Features

### **Manager Authorization**
- Only authorized manager phone numbers can use manager commands
- Configured via `MANAGER_PHONE` in `.env`
- Unauthorized users get "❌ Unauthorized" message

### **Phone Number Matching**
- Matches last 10 digits to handle country codes
- Supports multiple manager phone formats

## 🧪 Testing the Manager System

### **Test Manager Commands:**
```bash
python test_whatsapp_integration.py
# Choose option 2 for interactive testing
# Use manager phone number from .env
```

### **Sample Test Flow:**
1. Submit leave as employee: `emp +918106778477 I need 2 days leave`
2. Approve as manager: `mgr +918106778477 approve #1`
3. Check status: `mgr +918106778477 status #1`

## 📊 Manager Dashboard Commands

### **Quick Status Check:**
```
Manager: "List"
→ Shows all pending requests with quick approve/reject commands
```

### **Bulk Operations:**
```
Manager: "Approve #1"
Manager: "Approve #2" 
Manager: "Reject #3 Not enough coverage"
→ Process multiple requests quickly
```

## 🔧 Configuration

### **Environment Variables:**
```bash
# Manager Configuration
MANAGER_PHONE=+918106778477        # Manager's WhatsApp number
TWILIO_ACCOUNT_SID=your_sid        # Twilio credentials
TWILIO_AUTH_TOKEN=your_token       # Twilio credentials
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Twilio WhatsApp number
```

### **Multiple Managers:**
To support multiple managers, modify the `is_manager()` function:
```python
def is_manager(self, phone: str) -> bool:
    manager_phones = [
        os.getenv('MANAGER_PHONE'),
        os.getenv('MANAGER_PHONE_2'),
        os.getenv('HR_MANAGER_PHONE')
    ]
    # Check against all manager phones
```

## 🚀 Production Deployment

### **Deploy Both Webhooks:**
```bash
# Deploy employee webhook
heroku create hr-employee-webhook
git subtree push --prefix=employee heroku main

# Deploy manager webhook  
heroku create hr-manager-webhook
git subtree push --prefix=manager heroku main
```

### **Set Environment Variables:**
```bash
heroku config:set TWILIO_ACCOUNT_SID=your_sid --app hr-employee-webhook
heroku config:set TWILIO_ACCOUNT_SID=your_sid --app hr-manager-webhook
```

### **Configure Twilio Production Webhooks:**
- Employee: `https://hr-employee-webhook.herokuapp.com/webhook`
- Manager: `https://hr-manager-webhook.herokuapp.com/manager-webhook`

## 🎯 Key Benefits

✅ **Instant Notifications** - Managers get immediate WhatsApp alerts  
✅ **AI-Powered Insights** - Gemini analysis helps decision-making  
✅ **Employee Feedback** - Automatic approval/rejection notifications  
✅ **Substitute Management** - Streamlined substitute assignment  
✅ **Command-Based** - Simple text commands for quick actions  
✅ **Secure** - Phone-based authorization  
✅ **Scalable** - Separate webhooks for different user types  

## 🔍 Troubleshooting

### **Manager Not Receiving Notifications:**
1. Check `MANAGER_PHONE` in `.env`
2. Verify Twilio account balance
3. Ensure manager joined WhatsApp sandbox

### **Employee Not Getting Approval Messages:**
1. Check employee phone number in `employees.xlsx`
2. Verify phone number format (+country code)
3. Check Flask console logs for errors

### **Commands Not Working:**
1. Verify manager phone authorization
2. Check command format (case-insensitive)
3. Ensure leave ID exists

---

**Ready to revolutionize your HR approvals with WhatsApp? Start with the setup above! 🚀**