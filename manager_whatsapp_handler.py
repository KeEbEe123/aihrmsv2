"""
Manager WhatsApp Handler - For approving/rejecting leaves via WhatsApp
Production-ready separate webhook for managers
"""
import os
import re
from typing import Dict, Optional
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv

from integrated_hr_agent import IntegratedHRAgent

load_dotenv()

# Global instance to maintain session state across requests
manager_handler_instance = None

class ManagerWhatsAppHandler:
    def __init__(self):
        self.hr_agent = IntegratedHRAgent()
        self.twilio_client = TwilioClient(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_from = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        
        # Manager sessions for tracking approval workflow
        if not hasattr(ManagerWhatsAppHandler, '_manager_sessions'):
            ManagerWhatsAppHandler._manager_sessions = {}
    
    @property
    def manager_sessions(self):
        return ManagerWhatsAppHandler._manager_sessions
    
    def is_manager(self, phone: str) -> bool:
        """Check if phone number belongs to a manager"""
        manager_phone = os.getenv('MANAGER_PHONE', '').replace('+', '').replace(' ', '')
        clean_phone = phone.replace('+', '').replace(' ', '')
        
        # Match last 10 digits
        return manager_phone[-10:] == clean_phone[-10:] if len(manager_phone) >= 10 else False
    
    def send_whatsapp_message(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp message via Twilio"""
        try:
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            self.twilio_client.messages.create(
                from_=self.twilio_from,
                to=to_phone,
                body=message
            )
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def parse_manager_command(self, message: str) -> Dict:
        """Parse manager commands from WhatsApp message"""
        message_lower = message.lower().strip()
        
        # Check for approval commands
        if any(word in message_lower for word in ['approve', 'accept', 'yes']):
            # Extract leave ID
            leave_id_match = re.search(r'#?(\d+)', message)
            if leave_id_match:
                return {
                    'action': 'approve',
                    'leave_id': int(leave_id_match.group(1))
                }
        
        # Check for rejection commands
        elif any(word in message_lower for word in ['reject', 'deny', 'no']):
            leave_id_match = re.search(r'#?(\d+)', message)
            if leave_id_match:
                return {
                    'action': 'reject',
                    'leave_id': int(leave_id_match.group(1)),
                    'reason': message  # Full message as reason
                }
        
        # Check for substitute assignment
        elif 'assign' in message_lower:
            # Pattern: "assign [name] to #[id]"
            assign_match = re.search(r'assign\s+(.+?)\s+to\s+#?(\d+)', message_lower)
            if assign_match:
                return {
                    'action': 'assign',
                    'substitute_name': assign_match.group(1).strip(),
                    'leave_id': int(assign_match.group(2))
                }
        
        # Check for status inquiry
        elif any(word in message_lower for word in ['status', 'check', 'info']):
            leave_id_match = re.search(r'#?(\d+)', message)
            if leave_id_match:
                return {
                    'action': 'status',
                    'leave_id': int(leave_id_match.group(1))
                }
        
        # Check for help
        elif 'help' in message_lower or 'commands' in message_lower:
            return {'action': 'help'}
        
        # Check for list pending leaves
        elif any(word in message_lower for word in ['list', 'pending', 'show']):
            return {'action': 'list'}
        
        return {'action': 'unknown'}
    
    def handle_manager_message(self, phone: str, message: str) -> str:
        """Handle manager WhatsApp messages"""
        # Check if user is authorized manager
        if not self.is_manager(phone):
            return "❌ Unauthorized. This service is only available to managers."
        
        command = self.parse_manager_command(message)
        action = command.get('action')
        
        print(f"DEBUG: Manager command - Action: {action}, Command: {command}")
        
        if action == 'approve':
            return self.approve_leave(command['leave_id'])
        
        elif action == 'reject':
            return self.reject_leave(command['leave_id'], command.get('reason', ''))
        
        elif action == 'assign':
            return self.assign_substitute(command['leave_id'], command['substitute_name'])
        
        elif action == 'status':
            return self.get_leave_status(command['leave_id'])
        
        elif action == 'list':
            return self.list_pending_leaves()
        
        elif action == 'help':
            return self.get_help_message()
        
        else:
            return self.get_help_message()
    
    def approve_leave(self, leave_id: int) -> str:
        """Approve a leave request"""
        # Get AI analysis first
        ai_result = self.hr_agent.get_ai_analysis(leave_id)
        if ai_result['status'] != 'success':
            return f"❌ Error: {ai_result['message']}"
        
        # Approve the leave
        result = self.hr_agent.approve_leave(leave_id)
        if result['status'] != 'success':
            return f"❌ Error approving leave: {result['message']}"
        
        # Get suggested substitutes
        substitutes = ai_result.get('substitutes', [])
        
        # Notify the employee
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
✅ Great News! Your leave request #{leave_id} has been APPROVED!

📅 Days: {ai_result['leave_days']} days
📝 Reason: {ai_result['reason']}

Your substitute teacher will be assigned shortly. You'll receive confirmation once everything is set up.

Enjoy your time off! 🌟
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        # Prepare substitute assignment message for manager
        substitute_list = "\n".join([f"• {sub}" for sub in substitutes]) if substitutes else "• No substitutes available"
        
        return f"""
✅ Leave #{leave_id} APPROVED successfully!

👤 Employee: {ai_result['teacher_name']}
📅 Days: {ai_result['leave_days']} days

Employee has been notified via WhatsApp.

🔄 Next Step: Assign Substitute
Available substitutes:
{substitute_list}

To assign a substitute, reply:
"Assign [substitute name] to #{leave_id}"

Example: "Assign Priya Sharma to #{leave_id}"
        """.strip()
    
    def reject_leave(self, leave_id: int, reason: str) -> str:
        """Reject a leave request"""
        # Get leave details first
        ai_result = self.hr_agent.get_ai_analysis(leave_id)
        if ai_result['status'] != 'success':
            return f"❌ Error: {ai_result['message']}"
        
        # Reject the leave
        result = self.hr_agent.reject_leave(leave_id, reason)
        if result['status'] != 'success':
            return f"❌ Error rejecting leave: {result['message']}"
        
        # Notify the employee
        employee_phone = self.get_employee_phone_by_leave_id(leave_id)
        if employee_phone:
            employee_msg = f"""
❌ Leave Request Update

Your leave request #{leave_id} has been reviewed and unfortunately cannot be approved at this time.

📅 Requested: {ai_result['leave_days']} days
📝 Reason: {ai_result['reason']}

💬 Manager's feedback: {reason}

Please contact your manager directly to discuss alternative arrangements or resubmit with different dates.
            """.strip()
            
            self.send_whatsapp_message(employee_phone, employee_msg)
        
        return f"""
❌ Leave #{leave_id} REJECTED

👤 Employee: {ai_result['teacher_name']} has been notified via WhatsApp.
📝 Rejection reason: {reason}

The employee can resubmit a new request if needed.
        """.strip()
    
    def assign_substitute(self, leave_id: int, substitute_name: str) -> str:
        """Assign a substitute teacher to approved leave"""
        result = self.hr_agent.assign_substitute(leave_id, substitute_name)
        if result['status'] != 'success':
            return f"❌ Error: {result['message']}"
        
        # Notify the substitute (if they have WhatsApp)
        substitute = self.hr_agent.find_teacher_by_name(substitute_name)
        if substitute and substitute.get('phone'):
            substitute_phone = f"whatsapp:+{substitute['phone']}"
            substitute_msg = f"""
🔔 Substitute Assignment

You have been assigned as a substitute teacher for leave request #{leave_id}.

Please confirm your availability by replying:
• "Accept #{leave_id}" to confirm
• "Decline #{leave_id}" if not available

Thank you!
            """.strip()
            
            self.send_whatsapp_message(substitute_phone, substitute_msg)
        
        return f"""
✅ Substitute Assigned Successfully!

👤 Substitute: {substitute_name}
📋 Leave ID: #{leave_id}

The substitute has been notified and will confirm their availability.
        """.strip()
    
    def get_leave_status(self, leave_id: int) -> str:
        """Get status of a leave request"""
        result = self.hr_agent.get_leave_status(leave_id)
        if result['status'] != 'success':
            return f"❌ Error: {result['message']}"
        
        leave = result['leave']
        substitutions = result['substitutions']
        
        status_msg = f"""
📋 Leave Request #{leave['id']} Status

👤 Employee: {leave['teacher']}
📅 Days: {leave['days']} days
📝 Reason: {leave['reason']}
🔄 Status: {leave['status'].upper()}
        """
        
        if substitutions:
            status_msg += "\n\n🔄 Substitutions:"
            for sub in substitutions:
                status_msg += f"\n• {sub['substitute']} - {sub['status'].upper()}"
        
        return status_msg.strip()
    
    def list_pending_leaves(self) -> str:
        """List all pending leave requests"""
        pending_leaves = [l for l in self.hr_agent.leaves if l.status == 'pending']
        
        if not pending_leaves:
            return "📋 No pending leave requests at the moment."
        
        msg = "📋 Pending Leave Requests:\n\n"
        for leave in pending_leaves:
            msg += f"#{leave.id} - {leave.teacher_name}\n"
            msg += f"📅 {leave.days} days\n"
            msg += f"📝 {leave.reason}\n"
            msg += f"Commands: 'Approve #{leave.id}' or 'Reject #{leave.id} [reason]'\n\n"
        
        return msg.strip()
    
    def get_employee_phone_by_leave_id(self, leave_id: int) -> Optional[str]:
        """Get employee phone number by leave ID"""
        # Find the leave request
        leave = next((l for l in self.hr_agent.leaves if l.id == leave_id), None)
        if not leave:
            return None
        
        # Find employee in database
        employee = self.hr_agent.find_teacher_by_name(leave.teacher_name)
        if employee:
            phone = str(employee.get('phone', ''))
            return f"whatsapp:+{phone}" if phone else None
        
        return None
    
    def get_help_message(self) -> str:
        """Get help message for managers"""
        return """
🤖 Manager Commands Help

📋 Leave Management:
• "List" - Show pending requests
• "Approve #123" - Approve leave request
• "Reject #123 [reason]" - Reject with reason
• "Status #123" - Check leave status

🔄 Substitute Assignment:
• "Assign [name] to #123" - Assign substitute

📞 Examples:
• "List"
• "Approve #1"
• "Reject #1 Not enough coverage"
• "Status #1"
• "Assign Priya Sharma to #1"

Type "help" anytime for this menu.
        """.strip()

def create_manager_webhook_app():
    """Create Flask app for manager webhook"""
    app = Flask(__name__)
    
    @app.route('/manager-webhook', methods=['POST', 'GET'])
    def manager_webhook():
        """Handle manager WhatsApp messages"""
        global manager_handler_instance
        
        # Use singleton pattern to maintain session state
        if manager_handler_instance is None:
            manager_handler_instance = ManagerWhatsAppHandler()
        
        manager_handler = manager_handler_instance
        
        print(f"Manager webhook called with method: {request.method}")
        print(f"Request data: {request.values}")
        
        if request.method == 'GET':
            return "Manager webhook is working!", 200
        
        try:
            # Get message details
            incoming_msg = request.values.get('Body', '').strip()
            from_number = request.values.get('From', '')
            
            print(f"Manager message: '{incoming_msg}' from {from_number}")
            
            # Extract phone number
            phone = from_number.replace('whatsapp:', '')
            print(f"Manager phone: {phone}")
            
            # Handle the message
            response_msg = manager_handler.handle_manager_message(phone, incoming_msg)
            print(f"Manager response: {response_msg}")
            
            # Create response
            resp = MessagingResponse()
            resp.message(response_msg)
            
            return Response(str(resp), mimetype='text/xml')
            
        except Exception as e:
            print(f"Error in manager webhook: {e}")
            import traceback
            traceback.print_exc()
            resp = MessagingResponse()
            resp.message("❌ Sorry, there was an error processing your request. Please try again.")
            return Response(str(resp), mimetype='text/xml')
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "manager-webhook"}
    
    return app

if __name__ == '__main__':
    app = create_manager_webhook_app()
    print("🚀 Starting Manager WhatsApp Handler...")
    print("📱 Manager Webhook URL: http://localhost:5001/manager-webhook")
    print("🌐 Make sure to expose this via ngrok for Twilio")
    app.run(debug=True, host='0.0.0.0', port=5001)  # Different port for manager webhook