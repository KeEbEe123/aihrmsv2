"""
Start WhatsApp HR System - Runs both employee and manager webhooks
"""
import subprocess
import sys
import time
import os
from threading import Thread

def run_employee_webhook():
    """Run employee WhatsApp webhook"""
    print("🚀 Starting Employee WhatsApp Handler on port 5000...")
    subprocess.run([sys.executable, "whatsapp_hr_agent.py"])

def run_manager_webhook():
    """Run manager WhatsApp webhook"""
    print("🚀 Starting Manager WhatsApp Handler on port 5001...")
    subprocess.run([sys.executable, "manager_whatsapp_handler.py"])

def main():
    print("🎯 WhatsApp HR System Startup")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run 'python setup_whatsapp.py' first")
        return
    
    print("📱 Starting dual webhook system...")
    print("   • Employee webhook: http://localhost:5000/webhook")
    print("   • Manager webhook: http://localhost:5001/manager-webhook")
    print()
    print("🌐 Expose both ports via ngrok:")
    print("   Terminal 3: ngrok http 5000")
    print("   Terminal 4: ngrok http 5001")
    print()
    print("⚙️  Configure Twilio webhooks:")
    print("   • Employee WhatsApp: https://your-ngrok-url.ngrok-free.dev/webhook")
    print("   • Manager WhatsApp: https://your-manager-ngrok-url.ngrok-free.dev/manager-webhook")
    print()
    print("Press Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Start both webhooks in separate threads
        employee_thread = Thread(target=run_employee_webhook, daemon=True)
        manager_thread = Thread(target=run_manager_webhook, daemon=True)
        
        employee_thread.start()
        time.sleep(2)  # Give employee webhook time to start
        manager_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down WhatsApp HR System...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()