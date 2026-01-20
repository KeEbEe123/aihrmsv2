"""
Start Unified WhatsApp HR System - Single webhook handles everything
"""
import subprocess
import sys
import os

def main():
    print("🎯 Unified WhatsApp HR System")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run 'python setup_whatsapp.py' first")
        return
    
    print("📱 Starting unified webhook system...")
    print("   • Single webhook handles both employees and managers")
    print("   • Automatic routing based on phone number and message content")
    print("   • Webhook URL: http://localhost:5000/webhook")
    print()
    print("🌐 Expose via ngrok:")
    print("   Terminal 2: ngrok http 5000")
    print()
    print("⚙️  Configure Twilio webhook:")
    print("   • WhatsApp Sandbox: https://your-ngrok-url.ngrok-free.dev/webhook")
    print()
    print("🧪 Test Messages:")
    print("   Employee: 'I need 3 days leave for family emergency'")
    print("   Manager: 'List' or 'Approve #1' or 'Reject #1 reason'")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start the unified webhook
        subprocess.run([sys.executable, "unified_whatsapp_handler.py"])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down WhatsApp HR System...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()