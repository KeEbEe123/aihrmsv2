"""
Demo: Integrated AI-Powered HRMS with LangChain + Gemini
Simulates the complete leave management workflow
"""
from integrated_hr_agent import IntegratedHRAgent

def print_separator():
    print("\n" + "="*70 + "\n")

def demo_complete_workflow():
    """Demonstrate the complete leave management workflow"""
    
    print("🤖 AI-Powered HRMS - Complete Leave Management Demo")
    print("Using LangChain + Google Gemini for intelligent decisions")
    print_separator()
    
    # Initialize the agent
    agent = IntegratedHRAgent("employees.xlsx")
    
    # Scenario 1: Teacher submits leave request
    print("📝 STEP 1: Teacher submits leave request")
    print("-" * 70)
    teacher_name = input("Enter teacher name (or press Enter for 'Ravi Kumar'): ").strip()
    if not teacher_name:
        teacher_name = "Ravi Kumar"
    
    leave_days = input("Enter number of leave days (or press Enter for '3'): ").strip()
    leave_days = int(leave_days) if leave_days else 3
    
    reason = input("Enter reason (or press Enter for 'Family emergency'): ").strip()
    if not reason:
        reason = "Family emergency"
    
    result = agent.submit_leave_request(teacher_name, leave_days, reason)
    print(f"\n✅ {result['message']}")
    
    if result['status'] == 'error':
        print("❌ Demo cannot continue. Please check teacher name in employees.xlsx")
        return
    
    leave_id = result['leave_id']
    print_separator()
    
    # Scenario 2: HOD reviews with AI assistance
    print("🎯 STEP 2: HOD reviews leave request with AI assistance")
    print("-" * 70)
    input("Press Enter to get AI analysis...")
    
    print("\n🤖 AI Agent analyzing request...")
    analysis = agent.get_ai_analysis(leave_id)
    
    if analysis['status'] == 'error':
        print(f"❌ {analysis['message']}")
        return
    
    print(f"\n📊 AI ANALYSIS FOR LEAVE #{leave_id}")
    print("=" * 70)
    print(f"Teacher: {analysis['teacher_name']}")
    print(f"Days Requested: {analysis['leave_days']}")
    print(f"Reason: {analysis['reason']}")
    print("\n" + "─" * 70)
    print(analysis['ai_analysis'])
    print("─" * 70)
    
    # HOD makes the decision
    print("\n🤔 HOD Decision Time")
    decision = input("\nApprove this leave request? (y/n): ").strip().lower()
    
    if decision == 'y':
        result = agent.approve_leave(leave_id)
        print(f"\n✅ {result['message']}")
        leave_approved = True
    else:
        rejection_reason = input("Reason for rejection (optional): ").strip()
        result = agent.reject_leave(leave_id, rejection_reason)
        print(f"\n❌ {result['message']}")
        if rejection_reason:
            print(f"Reason: {rejection_reason}")
        leave_approved = False
    
    print_separator()
    
    # Scenario 3: Assign substitute (if approved)
    if leave_approved:
        print("👥 STEP 3: Assign substitute teacher")
        print("-" * 70)
        substitute = input("Enter substitute teacher name (or press Enter for 'Priya Sharma'): ").strip()
        if not substitute:
            substitute = "Priya Sharma"
        
        sub_result = agent.assign_substitute(leave_id, substitute)
        print(f"\n✅ {sub_result['message']}")
        
        if sub_result['status'] == 'success':
            print_separator()
            
            # Scenario 4: Substitute confirms
            print("✔️ STEP 4: Substitute confirms acceptance")
            print("-" * 70)
            input(f"Press Enter for {substitute} to confirm substitution...")
            
            confirm_result = agent.confirm_substitution(sub_result['substitution_id'])
            print(f"\n✅ {confirm_result['message']}")
    else:
        print("⚠️ Leave not approved, skipping substitute assignment")
    
    print_separator()
    
    # Final status
    print("📋 FINAL STATUS")
    print("-" * 70)
    status = agent.get_leave_status(leave_id)
    leave_info = status['leave']
    print(f"Leave ID: #{leave_info['id']}")
    print(f"Teacher: {leave_info['teacher']}")
    print(f"Days: {leave_info['days']}")
    print(f"Reason: {leave_info['reason']}")
    print(f"Status: {leave_info['status'].upper()}")
    
    if status['substitutions']:
        print(f"\nSubstitutes:")
        for sub in status['substitutions']:
            print(f"  - {sub['substitute']} (Status: {sub['status']})")
    
    print_separator()
    print("✨ Demo completed!")

def demo_interactive():
    """Interactive mode for testing multiple scenarios"""
    print("🤖 AI-Powered HRMS - Interactive Mode")
    print_separator()
    
    agent = IntegratedHRAgent("employees.xlsx")
    
    while True:
        print("\nOptions:")
        print("1. Submit leave request")
        print("2. Get AI analysis and approve/reject")
        print("3. Assign substitute")
        print("4. Confirm substitution")
        print("5. Check leave status")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            name = input("Teacher name: ")
            days = int(input("Leave days: "))
            reason = input("Reason: ")
            result = agent.submit_leave_request(name, days, reason)
            print(f"\n{result['message']}")
            
        elif choice == "2":
            leave_id = int(input("Leave ID: "))
            analysis = agent.get_ai_analysis(leave_id)
            
            if analysis['status'] == 'error':
                print(f"\n❌ {analysis['message']}")
            else:
                print(f"\n📊 AI ANALYSIS FOR LEAVE #{leave_id}")
                print("=" * 70)
                print(f"Teacher: {analysis['teacher_name']}")
                print(f"Days: {analysis['leave_days']}")
                print(f"Reason: {analysis['reason']}")
                print("\n" + "─" * 70)
                print(analysis['ai_analysis'])
                print("─" * 70)
                
                # HOD decision
                decision = input("\nApprove this leave? (y/n): ").strip().lower()
                if decision == 'y':
                    result = agent.approve_leave(leave_id)
                    print(f"\n✅ {result['message']}")
                elif decision == 'n':
                    reason = input("Rejection reason (optional): ").strip()
                    result = agent.reject_leave(leave_id, reason)
                    print(f"\n❌ {result['message']}")
                else:
                    print("\n⚠️ No action taken")
            
        elif choice == "3":
            leave_id = int(input("Leave ID: "))
            substitute = input("Substitute name: ")
            result = agent.assign_substitute(leave_id, substitute)
            print(f"\n{result['message']}")
            
        elif choice == "4":
            sub_id = int(input("Substitution ID: "))
            result = agent.confirm_substitution(sub_id)
            print(f"\n{result['message']}")
            
        elif choice == "5":
            leave_id = int(input("Leave ID: "))
            result = agent.get_leave_status(leave_id)
            if result['status'] == 'success':
                leave = result['leave']
                print(f"\nLeave #{leave['id']}: {leave['teacher']}")
                print(f"Status: {leave['status']}")
                print(f"Days: {leave['days']}, Reason: {leave['reason']}")
                if result['substitutions']:
                    print("Substitutes:")
                    for s in result['substitutions']:
                        print(f"  - {s['substitute']} ({s['status']})")
            else:
                print(f"\n{result['message']}")
                
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option")

if __name__ == "__main__":
    print("\nSelect demo mode:")
    print("1. Complete workflow demo (guided)")
    print("2. Interactive mode (manual testing)")
    
    mode = input("\nChoice (1 or 2): ").strip()
    print()
    
    if mode == "1":
        demo_complete_workflow()
    elif mode == "2":
        demo_interactive()
    else:
        print("Invalid choice. Running complete workflow demo...")
        demo_complete_workflow()
