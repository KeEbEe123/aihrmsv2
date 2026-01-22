@echo off
REM AI-Powered HRMS WhatsApp Handler - Deployment Script for Windows
REM This script helps you deploy to Render or test locally with Docker

echo ========================================================
echo AI-Powered HRMS WhatsApp Handler - Deployment Helper
echo ========================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed. Please install Git first.
    pause
    exit /b 1
)

echo [OK] Prerequisites check passed!
echo.

:menu
echo Choose deployment option:
echo 1) Test locally with Docker
echo 2) Build Docker image for production
echo 3) Deploy to Render (push to GitHub)
echo 4) Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto build
if "%choice%"=="3" goto render
if "%choice%"=="4" goto end
echo [ERROR] Invalid choice. Please try again.
echo.
goto menu

:local
echo.
echo Building and running Docker container locally...

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [INFO] Please edit .env file with your credentials.
    pause
)

REM Build image
echo Building Docker image...
docker build -t ai-hrms-whatsapp:latest .

REM Stop and remove existing container if it exists
docker stop ai-hrms-whatsapp >nul 2>&1
docker rm ai-hrms-whatsapp >nul 2>&1

REM Run container
echo Starting container...
docker run -d --name ai-hrms-whatsapp -p 5000:5000 --env-file .env ai-hrms-whatsapp:latest

echo.
echo [SUCCESS] Container started successfully!
echo Webhook URL: http://localhost:5000/webhook
echo Health check: http://localhost:5000/health
echo.
echo To view logs: docker logs -f ai-hrms-whatsapp
echo To stop: docker stop ai-hrms-whatsapp
echo To remove: docker rm ai-hrms-whatsapp
echo.
pause
goto end

:build
echo.
echo Building production Docker image...
docker build -t ai-hrms-whatsapp:production .

echo.
echo [SUCCESS] Production image built successfully!
echo Image: ai-hrms-whatsapp:production
echo.
echo To test: docker run -p 5000:5000 --env-file .env ai-hrms-whatsapp:production
echo.
pause
goto end

:render
echo.
echo Preparing for Render deployment...

REM Check if git repo is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
)

REM Check for uncommitted changes
git diff-index --quiet HEAD -- >nul 2>&1
if errorlevel 1 (
    echo Committing changes...
    git add .
    git commit -m "Update for Render deployment"
)

echo.
echo [SUCCESS] Code is ready for deployment!
echo.
echo Next steps:
echo 1. Push to GitHub:
echo    git remote add origin https://github.com/yourusername/your-repo.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 2. Go to Render Dashboard: https://dashboard.render.com
echo 3. Click 'New +' -^> 'Web Service'
echo 4. Connect your GitHub repository
echo 5. Render will auto-detect Dockerfile
echo 6. Set environment variables in Render Dashboard
echo 7. Click 'Create Web Service'
echo.
echo See RENDER_DEPLOYMENT.md for detailed instructions
echo.
pause
goto end

:end
echo.
echo Done!
pause
