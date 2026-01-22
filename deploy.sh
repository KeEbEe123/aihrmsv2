#!/bin/bash

# AI-Powered HRMS WhatsApp Handler - Deployment Script
# This script helps you deploy to Render or test locally with Docker

set -e

echo "🚀 AI-Powered HRMS WhatsApp Handler - Deployment Helper"
echo "========================================================"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists git; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

# Menu
echo "Choose deployment option:"
echo "1) Test locally with Docker"
echo "2) Build Docker image for production"
echo "3) Deploy to Render (push to GitHub)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🐳 Building and running Docker container locally..."
        
        # Check if .env exists
        if [ ! -f .env ]; then
            echo "⚠️  .env file not found. Creating from .env.example..."
            cp .env.example .env
            echo "📝 Please edit .env file with your credentials before continuing."
            read -p "Press Enter after editing .env file..."
        fi
        
        # Build image
        echo "Building Docker image..."
        docker build -t ai-hrms-whatsapp:latest .
        
        # Run container
        echo "Starting container..."
        docker run -d \
            --name ai-hrms-whatsapp \
            -p 5000:5000 \
            --env-file .env \
            ai-hrms-whatsapp:latest
        
        echo ""
        echo "✅ Container started successfully!"
        echo "📱 Webhook URL: http://localhost:5000/webhook"
        echo "🏥 Health check: http://localhost:5000/health"
        echo ""
        echo "To view logs: docker logs -f ai-hrms-whatsapp"
        echo "To stop: docker stop ai-hrms-whatsapp"
        echo "To remove: docker rm ai-hrms-whatsapp"
        ;;
        
    2)
        echo ""
        echo "🏗️  Building production Docker image..."
        docker build -t ai-hrms-whatsapp:production .
        
        echo ""
        echo "✅ Production image built successfully!"
        echo "📦 Image: ai-hrms-whatsapp:production"
        echo ""
        echo "To test: docker run -p 5000:5000 --env-file .env ai-hrms-whatsapp:production"
        ;;
        
    3)
        echo ""
        echo "🚀 Preparing for Render deployment..."
        
        # Check if git repo is initialized
        if [ ! -d .git ]; then
            echo "Initializing git repository..."
            git init
            git add .
            git commit -m "Initial commit for Render deployment"
        fi
        
        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            echo "📝 Committing changes..."
            git add .
            git commit -m "Update for Render deployment"
        fi
        
        echo ""
        echo "✅ Code is ready for deployment!"
        echo ""
        echo "Next steps:"
        echo "1. Push to GitHub:"
        echo "   git remote add origin https://github.com/yourusername/your-repo.git"
        echo "   git branch -M main"
        echo "   git push -u origin main"
        echo ""
        echo "2. Go to Render Dashboard: https://dashboard.render.com"
        echo "3. Click 'New +' → 'Web Service'"
        echo "4. Connect your GitHub repository"
        echo "5. Render will auto-detect Dockerfile"
        echo "6. Set environment variables in Render Dashboard"
        echo "7. Click 'Create Web Service'"
        echo ""
        echo "📖 See RENDER_DEPLOYMENT.md for detailed instructions"
        ;;
        
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✨ Done!"
