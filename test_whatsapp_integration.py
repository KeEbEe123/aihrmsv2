"""
Test WhatsApp Integration - Simulate WhatsApp messages for testing
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from whatsapp_hr_agent import WhatsAppHRAgent
from manager_whatsapp_handler import ManagerWhatsAppHandler

load_dotenv()

class WhatsAppTester:
    def __init__(self):
        self.employee_agent = WhatsAppHRAgent()
        self.manager_handler = ManagerWhatsAppHandler()
    
    def simulate_employee_message(self, phone: str, message: str) -> str:
        """Simulate an employee WhatsApp message"""
        print(f"\n📱 Employee ({phone}): {message}")
        
        # Find employee
        employee = self.employee_agent.find_employee_by_phone(phone)
        
        if not employee:
            response = "❌ Sorry, I couldn't find your employee record."
        else:
            response = self.employee_agent.handle_leave_application(phone, message, employee)
        
        print(f"🤖 Bot Response: {response}")
        return response
    
    def simulate_manager_message(self, phone: str, message: str) -> str:
        """Simulate a manager WhatsApp message"""
        print(f"\n👨‍💼 Manager ({phone}): {message}")
        
        response = self.manager_handler.handle_manager_message(phone, message)
        
        print(f"🤖 Bot Response: {response}")
        return response
    
    def run_complete_workflow_test(self):
        """Test complete leave application workflow"""
        print("🧪 Testing Complete WhatsApp Leave Workflow")
        print("=" * 60)
        
        # Employee details (from sample data)
        employee_phone = "+1234567890"  # Ravi Kumar
        manager_phone = "+1234567899"   # Manager
        
        print("\n📋 Scenario: Employee applies for 3-day emergency leave")
        
        # Step 1: Employee initiates leave request
        self.simulate_employee_message(
            employee_phone, 
            "Hi, I need to apply for leave for 3 days due to family emergency"
        )
        
        # Step 2: Employee confirms details
        print("\n" + "-" * 40)
        print("Employee confirms the leave application...")
        self.simulate_employee_message(employee_phone, "yes")
        
        # Step 3: Manager receives notification and approves
        print("\n" + "-" * 40)
        print("Manager reviews and approves the leave...")
        self.simulate_manager_message(manager_phone, "approve #1")
        
        # Step 4: Check final status
        print("\n" + "-" * 40)
        print("Checking final leave status...")
        self.simulate_manager_message(manager_phone, "status #1")
        
        print("\n✅ Workflow test completed!")
    
    def run_interactive_test(self):
        """Interactive testing mode"""
        print("🧪 Interactive WhatsApp Testing Mode")
        print("=" * 50)
        print("Commands:")
        print("  emp <phone> <message>  - Send employee message")
        print("  mgr <phone> <message>  - Send manager message")
        print("  quit                   - Exit")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() == 'quit':
                    break
                
                parts = command.split(' ', 2)
                if len(parts) < 3:
                    print("❌ Invalid format. Use: emp/mgr <phone> <message>")
                    continue
                
                cmd_type, phone, message = parts
                
                if cmd_type.lower() == 'emp':
                    self.simulate_employee_message(phone, message)
                elif cmd_type.lower() == 'mgr':
                    self.simulate_manager_message(phone, message)
                else:
                    print("❌ Unknown command. Use 'emp' or 'mgr'")
                
            except KeyboardInterrupt:
                break
        
        print("\n👋 Testing session ended!")
    
    def test_message_parsing(self):
        """Test message parsing capabilities"""
        print("🧪 Testing Message Parsing")
        print("=" * 40)
        
        test_messages = [
            "I need 3 days leave for family emergency",
            "Apply for 2 days sick leave",
            "Want leave for 5 days due to medical reasons",
            "I need time off for 1 day because of personal work",
            "Leave application for 4 days - wedding in family"
        ]
        
        for msg in test_messages:
            print(f"\n📝 Message: {msg}")
            details = self.employee_agent.extract_leave_details(msg)
            print(f"🔍 Extracted: {details}")
    
    def show_sample_data(self):
        """Show sample employee data for testing"""
        print("📊 Sample Employee Data for Testing")
        print("=" * 50)
        
        try:
            import pandas as pd
            df = pd.read_excel("employees.xlsx")
            
            print("\n👥 Available Employees:")
            for _, emp in df.iterrows():
                print(f"  📞 {emp.get('phone', 'N/A')} - {emp.get('name', 'N/A')} ({emp.get('department', 'N/A')})")
            
            print(f"\n👨‍💼 Manager Phone: {os.getenv('MANAGER_PHONE', 'Not set')}")
            
        except Exception as e:
            print(f"❌ Error loading employee data: {e}")

def main():
    """Main testing function"""
    tester = WhatsAppTester()
    
    print("🧪 WhatsApp HR Agent Testing Suite")
    print("=" * 50)
    print("1. Complete Workflow Test")
    print("2. Interactive Testing")
    print("3. Message Parsing Test")
    print("4. Show Sample Data")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                tester.run_complete_workflow_test()
            elif choice == '2':
                tester.run_interactive_test()
            elif choice == '3':
                tester.test_message_parsing()
            elif choice == '4':
                tester.show_sample_data()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()