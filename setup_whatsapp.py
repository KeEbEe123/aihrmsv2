"""
WhatsApp Setup Script - Configures Twilio and creates necessary files
"""
import os
import pandas as pd
from dotenv import load_dotenv, set_key

def setup_environment():
    """Setup environment variables for WhatsApp integration"""
    print("🚀 WhatsApp HR Agent Setup")
    print("=" * 50)
    
    # Load existing .env
    load_dotenv()
    
    # Collect Twilio credentials
    print("\n📱 Twilio Configuration")
    print("Get these from: https://console.twilio.com/")
    
    account_sid = input("Enter Twilio Account SID: ").strip()
    auth_token = input("Enter Twilio Auth Token: ").strip()
    whatsapp_from = input("Enter Twilio WhatsApp From Number (e.g., whatsapp:+14155238886): ").strip()
    
    # Manager phone for notifications
    print("\n👨‍💼 Manager Configuration")
    manager_phone = input("Enter Manager's WhatsApp Number (e.g., +1234567890): ").strip()
    
    # Webhook URL (for production)
    print("\n🌐 Webhook Configuration")
    webhook_url = input("Enter your webhook URL (leave blank for local testing): ").strip()
    
    # Update .env file
    env_file = ".env"
    
    set_key(env_file, "TWILIO_ACCOUNT_SID", account_sid)
    set_key(env_file, "TWILIO_AUTH_TOKEN", auth_token)
    set_key(env_file, "TWILIO_WHATSAPP_FROM", whatsapp_from)
    set_key(env_file, "MANAGER_PHONE", manager_phone)
    
    if webhook_url:
        set_key(env_file, "WEBHOOK_URL", webhook_url)
    
    print("\n✅ Environment variables updated!")
    
    return {
        'account_sid': account_sid,
        'auth_token': auth_token,
        'whatsapp_from': whatsapp_from,
        'manager_phone': manager_phone,
        'webhook_url': webhook_url
    }

def update_employee_data():
    """Update employee data with phone numbers"""
    print("\n📊 Employee Data Setup")
    
    # Check if employees.xlsx exists
    if not os.path.exists("employees.xlsx"):
        print("❌ employees.xlsx not found!")
        create_sample = input("Create sample employee data? (y/n): ").lower().strip()
        
        if create_sample == 'y':
            create_sample_employees()
        else:
            print("Please ensure employees.xlsx exists with phone numbers.")
            return
    
    # Load and check employee data
    df = pd.read_excel("employees.xlsx")
    
    if 'phone' not in df.columns:
        print("❌ 'phone' column not found in employees.xlsx")
        add_phone = input("Add phone column with sample data? (y/n): ").lower().strip()
        
        if add_phone == 'y':
            # Add sample phone numbers
            sample_phones = [
                "+1234567890", "+1234567891", "+1234567892", 
                "+1234567893", "+1234567894"
            ]
            
            df['phone'] = sample_phones[:len(df)]
            df.to_excel("employees.xlsx", index=False)
            print("✅ Phone numbers added to employees.xlsx")
        else:
            print("Please add phone numbers manually to employees.xlsx")
    else:
        print("✅ Employee data looks good!")
    
    print(f"📋 Found {len(df)} employees in database")

def create_sample_employees():
    """Create sample employee data"""
    sample_data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Ravi Kumar', 'Priya Sharma', 'Amit Singh', 'Neha Patel', 'Suresh Reddy'],
        'phone': ['+1234567890', '+1234567891', '+1234567892', '+1234567893', '+1234567894'],
        'department': ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English'],
        'available_leaves': [15, 12, 18, 10, 20],
        'pending_work': ['Exam preparation', 'Lab setup', 'None', 'Research project', 'None'],
        'role_criticality': ['High', 'Medium', 'Low', 'High', 'Medium']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel("employees.xlsx", index=False)
    print("✅ Sample employee data created!")

def create_requirements():
    """Create requirements.txt for WhatsApp integration"""
    requirements = """
# Existing requirements
langchain-google-genai
pandas
python-dotenv
openpyxl

# WhatsApp integration requirements
flask
twilio
requests
gunicorn
"""
    
    # Read existing requirements
    existing_reqs = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            existing_reqs = f.read().strip().split('\n')
    
    # Add new requirements
    new_reqs = [
        "flask",
        "twilio", 
        "requests",
        "gunicorn"
    ]
    
    # Combine and deduplicate
    all_reqs = list(set(existing_reqs + new_reqs))
    all_reqs = [req for req in all_reqs if req.strip()]  # Remove empty lines
    
    with open("requirements.txt", "w") as f:
        f.write('\n'.join(sorted(all_reqs)))
    
    print("✅ Requirements updated!")

def create_deployment_files():
    """Create deployment configuration files"""
    
    # Create Procfile for Heroku
    procfile_content = """web: gunicorn whatsapp_hr_agent:app --bind 0.0.0.0:$PORT
manager: gunicorn manager_whatsapp_handler:create_manager_webhook_app() --bind 0.0.0.0:$PORT"""
    
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    
    # Create runtime.txt
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.0")
    
    print("✅ Deployment files created!")

def print_next_steps(config):
    """Print next steps for setup"""
    print("\n" + "=" * 50)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 50)
    
    print("\n1. 📱 Configure Twilio WhatsApp Sandbox:")
    print("   • Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
    print("   • Join sandbox by sending message to Twilio number")
    print(f"   • Set webhook URL to: {config.get('webhook_url', 'YOUR_WEBHOOK_URL')}/webhook")
    
    print("\n2. 🔧 Install Dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n3. 🚀 Run the Application:")
    print("   # For employee requests:")
    print("   python whatsapp_hr_agent.py")
    print("   ")
    print("   # For manager approvals (separate terminal):")
    print("   python manager_whatsapp_handler.py")
    
    print("\n4. 🧪 Test the Integration:")
    print("   • Send WhatsApp message: 'I need 3 days leave for family emergency'")
    print(f"   • Manager will receive notification at: {config['manager_phone']}")
    print("   • Manager can reply: 'Approve #1' or 'Reject #1 reason'")
    
    print("\n5. 🌐 For Production Deployment:")
    print("   • Deploy to Heroku/Railway/DigitalOcean")
    print("   • Update Twilio webhook URL")
    print("   • Set up proper database (Supabase)")
    
    print("\n6. 📋 Sample WhatsApp Commands:")
    print("   Employee: 'I want to apply for leave'")
    print("   Employee: 'Need 2 days sick leave'")
    print("   Manager: 'Approve #1'")
    print("   Manager: 'Reject #1 Not enough coverage'")
    print("   Manager: 'Status #1'")

def main():
    """Main setup function"""
    try:
        # Setup environment
        config = setup_environment()
        
        # Update employee data
        update_employee_data()
        
        # Create requirements
        create_requirements()
        
        # Create deployment files
        create_deployment_files()
        
        # Print next steps
        print_next_steps(config)
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")

if __name__ == "__main__":
    main()