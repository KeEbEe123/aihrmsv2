# WhatsApp HR Agent Setup Guide

Complete guide to integrate your HR agent with WhatsApp using Twilio.

## 🎯 What This Does

When a user sends a WhatsApp message like "I want to apply for a leave":

1. **Auto-fetch user details** from database using phone number
2. **Collect leave information** through conversational flow
3. **AI analysis** using your existing Gemini integration
4. **Manager notification** via WhatsApp with AI insights
5. **Manager approval/rejection** via WhatsApp commands
6. **Employee notification** of final decision

## 🚀 Quick Setup (5 Minutes)

### Step 1: Run Setup Script
```bash
python setup_whatsapp.py
```

This will:
- Configure Twilio credentials
- Set manager phone number
- Update employee data with phone numbers
- Create deployment files

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Twilio WhatsApp Sandbox

1. Go to [Twilio Console](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Join sandbox by sending "join <code>" to the Twilio WhatsApp number
3. Set webhook URL to: `YOUR_WEBHOOK_URL/webhook`

### Step 4: Start the Application
```bash
# Terminal 1 - Employee requests
python whatsapp_hr_agent.py

# Terminal 2 - Manager approvals  
python manager_whatsapp_handler.py
```

## 📱 How It Works

### Employee Flow
```
Employee: "I need 3 days leave for family emergency"
    ↓
Bot: "Hi Ravi Kumar! Leave application summary:
     👤 Employee: Ravi Kumar
     📅 Days: 3 days  
     📝 Reason: family emergency
     Reply YES to confirm"
    ↓
Employee: "yes"
    ↓
Bot: "✅ Leave Request #1 submitted! Manager notified."
```

### Manager Flow
```
Manager receives: "🔔 New Leave Request #1
                  👤 Employee: Ravi Kumar
                  📅 Days: 3 days
                  🤖 AI Analysis: [Gemini insights]"
    ↓
Manager: "approve #1"
    ↓
Bot: "✅ Leave #1 APPROVED! Employee notified.
     Next: Assign substitute from suggested list"
```

## 🔧 Configuration Files

### .env Variables
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token  
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Manager Configuration
MANAGER_PHONE=+1234567890

# Existing Google AI
GOOGLE_API_KEY=your_google_api_key
```

### Employee Database (employees.xlsx)
Required columns:
- `name` - Employee name
- `phone` - WhatsApp phone number (+1234567890)
- `department` - Department name
- `available_leaves` - Available leave days
- `pending_work` - Current pending work
- `role_criticality` - High/Medium/Low

## 🧪 Testing

### Option 1: Automated Test
```bash
python test_whatsapp_integration.py
```

### Option 2: Manual Testing
1. Send WhatsApp message to your Twilio number
2. Use test employee phone numbers from employees.xlsx
3. Test manager commands with manager phone number

### Sample Test Messages

**Employee Messages:**
- "I want to apply for leave"
- "Need 3 days sick leave"  
- "Apply for 2 days leave for family emergency"

**Manager Commands:**
- "approve #1" - Approve leave request #1
- "reject #1 not enough coverage" - Reject with reason
- "status #1" - Check leave status
- "help" - Show all commands

## 🌐 Production Deployment

### Option 1: Heroku
```bash
# Create Heroku app
heroku create your-hr-whatsapp-bot

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token
heroku config:set GOOGLE_API_KEY=your_key

# Deploy
git add .
git commit -m "WhatsApp HR Agent"
git push heroku main
```

### Option 2: Railway/DigitalOcean
1. Connect your GitHub repo
2. Set environment variables in dashboard
3. Deploy automatically

### Update Twilio Webhook
After deployment, update Twilio webhook URL to:
`https://your-app.herokuapp.com/webhook`

## 🔄 Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WhatsApp Integration                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📱 Employee WhatsApp                                        │
│  "I need 3 days leave"                                       │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │ Twilio Webhook  │────────▶│ Phone Lookup    │            │
│  │ /webhook        │         │ in Database     │            │
│  └─────────────────┘         └────────┬────────┘            │
│                                        │                      │
│                                        ▼                      │
│                              ┌─────────────────┐             │
│                              │ Conversation    │             │
│                              │ State Manager   │             │
│                              └────────┬────────┘             │
│                                       │                       │
│                                       ▼                       │
│                              ┌─────────────────┐             │
│                              │ Leave Request   │             │
│                              │ Submission      │             │
│                              └────────┬────────┘             │
│                                       │                       │
│                                       ▼                       │
│  ┌─────────────────────────────────────────────┐            │
│  │      AI AGENT (Your Existing System)        │            │
│  │  • LangChain + Google Gemini                │            │
│  │  • Employee data analysis                   │            │
│  │  • Leave policy evaluation                  │            │
│  │  • Substitute suggestions                   │            │
│  └──────────────────┬──────────────────────────┘            │
│                     │                                         │
│                     ▼                                         │
│         ┌───────────────────────┐                            │
│         │ Manager WhatsApp      │                            │
│         │ Notification          │                            │
│         │ + AI Analysis         │                            │
│         └───────────┬───────────┘                            │
│                     │                                         │
│  👨‍💼 Manager WhatsApp │                                         │
│  "approve #1"       │                                         │
│                     ▼                                         │
│         ┌───────────────────────┐                            │
│         │ Manager Webhook       │                            │
│         │ /manager-webhook      │                            │
│         └───────────┬───────────┘                            │
│                     │                                         │
│                     ▼                                         │
│         ┌───────────────────────┐                            │
│         │ Update Leave Status   │                            │
│         │ Notify Employee       │                            │
│         └───────────────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🎛️ Advanced Features

### 1. Multi-language Support
Add language detection and responses in local languages.

### 2. Rich Media Messages
Send images, documents, and formatted messages.

### 3. Integration with Calendar
Sync approved leaves with Google Calendar/Outlook.

### 4. Analytics Dashboard
Track leave patterns, approval rates, and AI decision accuracy.

### 5. Substitute Auto-Assignment
Automatically assign substitutes based on availability and expertise.

## 🔍 Troubleshooting

### Common Issues

**1. "Employee not found"**
- Check phone number format in employees.xlsx
- Ensure phone numbers include country code
- Verify WhatsApp number matches database

**2. "Twilio webhook not receiving messages"**
- Check webhook URL in Twilio console
- Ensure Flask app is running and accessible
- Verify Twilio credentials in .env

**3. "AI analysis not working"**
- Check GOOGLE_API_KEY in .env
- Verify Gemini API quota and billing
- Check internet connectivity

**4. "Manager not receiving notifications"**
- Verify MANAGER_PHONE in .env
- Check Twilio account balance
- Ensure manager joined WhatsApp sandbox

### Debug Mode
```bash
# Run with debug logging
FLASK_DEBUG=1 python whatsapp_hr_agent.py
```

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review Twilio console logs
3. Check Flask application logs
4. Test with the provided test script

## 🚀 Next Steps

After basic setup:
1. **Database Migration**: Move from Excel to Supabase
2. **Authentication**: Add user authentication
3. **Advanced AI**: Enhance AI decision-making
4. **Mobile App**: Create companion mobile app
5. **Enterprise Features**: Add advanced reporting and analytics

---

**Ready to revolutionize your HR processes with WhatsApp? Start with the quick setup above! 🚀**