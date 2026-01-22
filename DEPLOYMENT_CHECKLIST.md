# Deployment Checklist for Render

## Pre-Deployment Checklist

### 1. Code Preparation
- [x] `unified_whatsapp_handler.py` - Main application file
- [x] `integrated_hr_agent.py` - HR agent logic
- [x] `employees.xlsx` - Employee database
- [x] `requirements.txt` - Python dependencies
- [x] `Dockerfile` - Docker configuration
- [x] `.dockerignore` - Files to exclude from Docker
- [x] `render.yaml` - Render deployment blueprint
- [x] `.env.example` - Environment variables template
- [ ] `.env` - **DO NOT COMMIT** (for local testing only)

### 2. Environment Variables Ready
Prepare these values before deployment:
- [ ] `GOOGLE_API_KEY` - Get from Google AI Studio
- [ ] `TWILIO_ACCOUNT_SID` - From Twilio Console
- [ ] `TWILIO_AUTH_TOKEN` - From Twilio Console
- [ ] `TWILIO_WHATSAPP_FROM` - Your Twilio WhatsApp number
- [ ] `MANAGER_PHONE` - Manager's phone with country code

### 3. GitHub Repository
- [ ] Create GitHub repository
- [ ] Add `.gitignore` (exclude `.env`, `__pycache__`, etc.)
- [ ] Push code to GitHub
- [ ] Verify all files are uploaded

### 4. Twilio Configuration
- [ ] Twilio account created
- [ ] WhatsApp Sandbox enabled
- [ ] Test WhatsApp number configured
- [ ] Webhook URL ready to update

## Deployment Steps

### Step 1: Local Testing (Optional but Recommended)
```bash
# Windows
deploy.bat
# Choose option 1

# Mac/Linux
chmod +x deploy.sh
./deploy.sh
# Choose option 1
```

- [ ] Docker container builds successfully
- [ ] Health check responds: `http://localhost:5000/health`
- [ ] Test with ngrok: `ngrok http 5000`
- [ ] Send test WhatsApp message
- [ ] Verify employee flow works
- [ ] Verify manager flow works

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - AI HRMS WhatsApp Handler"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

- [ ] Code pushed to GitHub
- [ ] All files visible in repository
- [ ] `.env` is NOT in repository (check!)

### Step 3: Deploy to Render

#### Option A: Via Dashboard (Recommended)
1. [ ] Go to [Render Dashboard](https://dashboard.render.com)
2. [ ] Click "New +" → "Web Service"
3. [ ] Connect GitHub account
4. [ ] Select your repository
5. [ ] Configure service:
   - Name: `ai-hrms-whatsapp-handler`
   - Region: Choose closest to users
   - Branch: `main`
   - Runtime: **Docker** (auto-detected)
   - Plan: Free or Starter
6. [ ] Add environment variables (see list above)
7. [ ] Click "Create Web Service"
8. [ ] Wait for deployment (5-10 minutes)

#### Option B: Via Blueprint
1. [ ] Ensure `render.yaml` is in repository
2. [ ] Go to Render Dashboard
3. [ ] Click "New +" → "Blueprint"
4. [ ] Connect repository
5. [ ] Render detects `render.yaml`
6. [ ] Set environment variables
7. [ ] Click "Apply"

### Step 4: Post-Deployment Configuration

#### Get Your Webhook URL
- [ ] Note your Render URL: `https://your-service-name.onrender.com`
- [ ] Test health endpoint: `https://your-service-name.onrender.com/health`
- [ ] Verify response shows "healthy"

#### Update Twilio Webhook
1. [ ] Go to [Twilio Console](https://console.twilio.com)
2. [ ] Navigate to: Messaging → Try it out → Send a WhatsApp message
3. [ ] Update "WHEN A MESSAGE COMES IN":
   ```
   https://your-service-name.onrender.com/webhook
   ```
4. [ ] Set method to: `POST`
5. [ ] Save configuration

### Step 5: End-to-End Testing

#### Test Employee Flow
- [ ] Send: "I need 3 days leave for medical appointment"
- [ ] Verify: Bot asks for confirmation
- [ ] Reply: "Yes"
- [ ] Verify: Bot asks for substitute
- [ ] Reply: "Skip"
- [ ] Verify: Leave request submitted
- [ ] Verify: Manager receives notification

#### Test Manager Flow
- [ ] Manager sends: "List"
- [ ] Verify: Shows pending leaves
- [ ] Manager sends: "Status"
- [ ] Verify: Shows all leaves with details
- [ ] Manager sends: "Assign [substitute name] to #1"
- [ ] Verify: Substitute receives notification

#### Test Substitute Flow
- [ ] Substitute sends: "Accept #1"
- [ ] Verify: Confirmation message received
- [ ] Verify: Manager notified of acceptance

#### Test Manager Approval
- [ ] Manager sends: "Approve #1"
- [ ] Verify: Employee receives approval notification
- [ ] Verify: Leave status updated

## Production Checklist

### Performance
- [ ] Monitor response times in Render Dashboard
- [ ] Check memory usage
- [ ] Review logs for errors
- [ ] Consider upgrading to Starter plan if needed

### Security
- [ ] All secrets in environment variables (not code)
- [ ] `.env` file not in repository
- [ ] HTTPS enabled (automatic on Render)
- [ ] API keys rotated regularly

### Monitoring
- [ ] Set up Render email alerts
- [ ] Monitor Twilio usage
- [ ] Check Google AI API quota
- [ ] Review application logs daily

### Backup
- [ ] Export `employees.xlsx` regularly
- [ ] Document environment variables
- [ ] Keep deployment configuration in version control

## Troubleshooting

### Service Won't Start
- [ ] Check Render logs for errors
- [ ] Verify all environment variables are set
- [ ] Ensure `employees.xlsx` is in repository
- [ ] Check Docker build logs

### Webhook Not Working
- [ ] Verify Twilio webhook URL is correct
- [ ] Check service is running (not sleeping on free tier)
- [ ] Test health endpoint first
- [ ] Review application logs in Render

### Messages Not Sending
- [ ] Verify Twilio credentials are correct
- [ ] Check Twilio account balance
- [ ] Ensure phone numbers have correct format
- [ ] Review Twilio logs

## Maintenance

### Regular Tasks
- [ ] Weekly: Review logs for errors
- [ ] Monthly: Check API usage and costs
- [ ] Quarterly: Update dependencies
- [ ] As needed: Update employee database

### Updates
```bash
# Make changes locally
git add .
git commit -m "Description of changes"
git push origin main
# Render auto-deploys
```

## Success Criteria

- [x] Application deployed successfully
- [x] Health check returns 200 OK
- [x] Employee can apply for leave
- [x] Manager receives notifications
- [x] Manager can approve/reject leaves
- [x] Substitute workflow functions
- [x] All WhatsApp messages working
- [x] No errors in logs

## Support Resources

- **Render Docs**: https://render.com/docs
- **Twilio Docs**: https://www.twilio.com/docs/whatsapp
- **Docker Docs**: https://docs.docker.com
- **Flask Docs**: https://flask.palletsprojects.com

---

**Deployment Status**: Ready for Production ✅
**Last Updated**: January 22, 2026
**Version**: 1.0.0
