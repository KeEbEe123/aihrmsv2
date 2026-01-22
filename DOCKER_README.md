# Docker Deployment Guide

## Local Docker Testing

### Build the Docker Image
```bash
docker build -t ai-hrms-whatsapp .
```

### Run the Container Locally
```bash
docker run -p 5000:5000 \
  -e GOOGLE_API_KEY="your_key" \
  -e TWILIO_ACCOUNT_SID="your_sid" \
  -e TWILIO_AUTH_TOKEN="your_token" \
  -e TWILIO_WHATSAPP_FROM="whatsapp:+14155238886" \
  -e MANAGER_PHONE="+919160066882" \
  ai-hrms-whatsapp
```

### Or use Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  whatsapp-handler:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
      - MANAGER_PHONE=${MANAGER_PHONE}
      - PORT=5000
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Run with:
```bash
docker-compose up -d
```

### Test the Container
```bash
# Health check
curl http://localhost:5000/health

# View logs
docker logs -f <container_id>

# Stop container
docker stop <container_id>
```

## Deploy to Render

### Method 1: Automatic Deployment
1. Push code to GitHub
2. Connect repository to Render
3. Render auto-detects Dockerfile
4. Set environment variables
5. Deploy!

### Method 2: Manual Docker Push
```bash
# Build for production
docker build -t ai-hrms-whatsapp:latest .

# Tag for registry
docker tag ai-hrms-whatsapp:latest registry.render.com/your-service/ai-hrms-whatsapp:latest

# Push to Render registry
docker push registry.render.com/your-service/ai-hrms-whatsapp:latest
```

## Files Included in Docker Image

### Essential Files
- `unified_whatsapp_handler.py` - Main Flask application
- `integrated_hr_agent.py` - HR agent with AI logic
- `employees.xlsx` - Employee database
- `requirements.txt` - Python dependencies

### Configuration Files
- `Dockerfile` - Docker build instructions
- `.dockerignore` - Files to exclude from image
- `render.yaml` - Render deployment blueprint
- `.env.example` - Environment variables template

## Environment Variables

Required variables for production:
```bash
GOOGLE_API_KEY=          # Google Gemini API key
TWILIO_ACCOUNT_SID=      # Twilio account SID
TWILIO_AUTH_TOKEN=       # Twilio auth token
TWILIO_WHATSAPP_FROM=    # Twilio WhatsApp number
MANAGER_PHONE=           # Manager's phone number
PORT=5000                # Application port (set by Render)
```

## Docker Image Details

- **Base Image**: python:3.11-slim
- **Size**: ~200-300 MB (optimized)
- **Exposed Port**: 5000
- **Health Check**: /health endpoint
- **Web Server**: Gunicorn with 2 workers, 4 threads

## Production Considerations

### Security
- Never include `.env` in Docker image
- Use environment variables for secrets
- Keep base image updated
- Run as non-root user (add to Dockerfile if needed)

### Performance
- Adjust Gunicorn workers based on CPU cores
- Use Redis for session management (future enhancement)
- Enable response caching
- Monitor memory usage

### Persistence
- Excel file is ephemeral (resets on restart)
- Consider PostgreSQL for production
- Use volume mounts for data persistence

## Troubleshooting

### Build Fails
```bash
# Clear Docker cache
docker builder prune

# Rebuild without cache
docker build --no-cache -t ai-hrms-whatsapp .
```

### Container Crashes
```bash
# Check logs
docker logs <container_id>

# Inspect container
docker inspect <container_id>

# Run interactively
docker run -it ai-hrms-whatsapp /bin/bash
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Use different port
docker run -p 8080:5000 ai-hrms-whatsapp
```

## Next Steps

1. ✅ Build Docker image locally
2. ✅ Test with ngrok for Twilio webhook
3. ✅ Push code to GitHub
4. ✅ Deploy to Render
5. ✅ Update Twilio webhook URL
6. ✅ Test end-to-end workflow

---

**Ready for Production Deployment!** 🚀
