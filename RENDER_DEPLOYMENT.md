# Render Deployment Guide for AI-Powered HRMS WhatsApp Handler

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: Have your API keys ready

## Quick Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Connect GitHub Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this code

2. **Configure Service**
   - **Name**: `ai-hrms-whatsapp-handler`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Runtime**: Docker
   - **Plan**: Free (or Starter for production)

3. **Set Environment Variables**
   Go to "Environment" tab and add:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   MANAGER_PHONE=+919160066882
   PORT=5000
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your service will be available at: `https://your-service-name.onrender.com`

### Option 2: Deploy via render.yaml Blueprint

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Deploy from Blueprint**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml`
   - Set environment variables in the dashboard
   - Click "Apply"

## Post-Deployment Configuration

### 1. Get Your Webhook URL
After deployment, your webhook URL will be:
```
https://your-service-name.onrender.com/webhook
```

### 2. Update Twilio WhatsApp Sandbox
1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to: Messaging → Try it out → Send a WhatsApp message
3. Update "WHEN A MESSAGE COMES IN" webhook to:
   ```
   https://your-service-name.onrender.com/webhook
   ```
4. Set HTTP method to: `POST`
5. Save configuration

### 3. Test Your Deployment

**Health Check:**
```bash
curl https://your-service-name.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "unified-whatsapp-handler",
  "timestamp": "2026-01-22T..."
}
```

**WhatsApp Test:**
Send a message to your Twilio WhatsApp number:
```
I need 3 days leave for medical appointment
```

## Important Notes

### Free Tier Limitations
- **Spin Down**: Free services sleep after 15 minutes of inactivity
- **First Request**: May take 30-60 seconds to wake up
- **Solution**: Upgrade to Starter plan ($7/month) for always-on service

### Environment Variables Security
- **Never commit** `.env` file to GitHub
- Set all sensitive variables in Render Dashboard
- Use Render's "Secret Files" for additional security

### Monitoring
- **Logs**: View real-time logs in Render Dashboard → Logs tab
- **Metrics**: Monitor CPU, memory, and request metrics
- **Alerts**: Set up email alerts for service failures

## Troubleshooting

### Service Won't Start
1. Check logs in Render Dashboard
2. Verify all environment variables are set
3. Ensure `employees.xlsx` is in repository
4. Check Docker build logs

### Webhook Not Responding
1. Verify webhook URL in Twilio is correct
2. Check service is running (not sleeping)
3. Test health endpoint first
4. Review application logs

### Database/Excel File Issues
1. Ensure `employees.xlsx` is included in repository
2. Check file permissions in Docker container
3. Verify file path in `integrated_hr_agent.py`

## Scaling for Production

### Recommended Upgrades
1. **Plan**: Upgrade to Starter ($7/month) or higher
2. **Workers**: Increase Gunicorn workers for more traffic
3. **Database**: Replace Excel with PostgreSQL for persistence
4. **Redis**: Add Redis for session management
5. **Monitoring**: Integrate Sentry for error tracking

### Performance Optimization
```dockerfile
# In Dockerfile, adjust Gunicorn settings:
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} \
    --workers 4 \
    --threads 8 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    unified_whatsapp_handler:app
```

## Continuous Deployment

### Auto-Deploy on Git Push
Render automatically deploys when you push to your main branch:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Deploy
In Render Dashboard:
1. Go to your service
2. Click "Manual Deploy" → "Deploy latest commit"

## Support Resources

- **Render Docs**: https://render.com/docs
- **Twilio Docs**: https://www.twilio.com/docs/whatsapp
- **Support**: Check Render Dashboard → Support

## Cost Estimate

### Free Tier
- **Cost**: $0/month
- **Limitations**: Sleeps after 15 min, 750 hours/month

### Starter Plan (Recommended)
- **Cost**: $7/month
- **Benefits**: Always-on, custom domains, more resources

### Professional Plan
- **Cost**: $25/month
- **Benefits**: More CPU/RAM, priority support

---

**Deployment Date**: January 2026
**Version**: 1.0
**Status**: Production Ready ✅
