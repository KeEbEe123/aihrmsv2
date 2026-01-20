"""
WhatsApp HR Agent - Twilio Integration
Handles WhatsApp messages for leave applications
"""
import os
import re
from datetime import datetime
from typing import Dict, Optional, Tuple
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv

from integrated_hr_agent import IntegratedHRAgent

load_dotenv()

app = Flask(__name__)

@app.before_request
def allow_twilio():
    pass


class WhatsAppHRAgent:
    def __init__(self):
        self.hr_agent = IntegratedHRAgent()
        self.twilio_client = TwilioClient(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_from = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        
        # Session storage for conversation state (in production, use Redis/Database)
        # Make this a class variable to persist across requests
        if not hasattr(WhatsAppHRAgent, '_user_sessions'):
            WhatsAppHRAgent._user_sessions = {}
    
    @property
    def user_sessions(self):
        return WhatsAppHRAgent._user_sessions
    
    def extract_phone_number(self, whatsapp_from: str) -> str:
        """Extract phone number from WhatsApp format"""
        # Remove 'whatsapp:' prefix
        return whatsapp_from.replace('whatsapp:', '')
    
    def find_employee_by_phone(self, phone: str) -> Optional[Dict]:
        """Find employee by phone number in database"""
        # Clean phone number (remove country codes, spaces, etc.)
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        # Search in Excel database
        for _, employee in self.hr_agent.df.iterrows():
            emp_phone = str(employee.get('phone', ''))
            clean_emp_phone = re.sub(r'[^\d]', '', emp_phone)
            
            # Match last 10 digits (handles country codes)
            if clean_phone[-10:] == clean_emp_phone[-10:]:
                return employee.to_dict()
        
        return None
    
    def get_manager_phone(self, employee: Dict) -> Optional[str]:
        """Get manager's phone number for notifications"""
        # In a real system, this would query the database for the manager
        # For demo, we'll use a default manager phone from env
        return os.getenv('MANAGER_PHONE', '+1234567890')
    
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
    
    def parse_leave_intent(self, message: str) -> bool:
        """Check if message contains leave application intent"""
        leave_keywords = [
            'leave', 'apply for leave', 'need leave', 'want leave',
            'sick leave', 'casual leave', 'emergency leave',
            'vacation', 'time off', 'absent'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in leave_keywords)
    
    def extract_leave_details(self, message: str) -> Dict:
        """Extract leave details from message using regex"""
        details = {}
        
        # Extract number of days
        days_match = re.search(r'(\d+)\s*days?', message.lower())
        if days_match:
            details['days'] = int(days_match.group(1))
        
        # Extract dates (basic patterns)
        date_patterns = [
            r'from\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'on\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, message.lower())
            if date_match:
                details['date'] = date_match.group(1)
                break
        
        # Extract reason (everything after "for", "because", "due to")
        reason_patterns = [
            r'for\s+(.+?)(?:\.|$)',
            r'because\s+(.+?)(?:\.|$)',
            r'due to\s+(.+?)(?:\.|$)',
            r'reason:?\s*(.+?)(?:\.|$)'
        ]
        
        for pattern in reason_patterns:
            reason_match = re.search(pattern, message.lower())
            if reason_match:
                details['reason'] = reason_match.group(1).strip()
                break
        
        return details
    
    def handle_leave_application(self, phone: str, message: str, employee: Dict) -> str:
        """Handle complete leave application flow"""
        session_key = phone
        
        # Special commands
        if message.lower().strip() in ['reset', 'restart', 'clear']:
            if session_key in self.user_sessions:
                del self.user_sessions[session_key]
            return f"Hi {employee['name']}! Session reset. How can I help you today?"
        
        # Initialize session if not exists
        if session_key not in self.user_sessions:
            self.user_sessions[session_key] = {
                'state': 'initial',
                'employee': employee,
                'leave_data': {}
            }
            print(f"DEBUG: Created new session for {phone}")
        
        session = self.user_sessions[session_key]
        state = session['state']
        
        print(f"DEBUG: Phone {phone}, State: {state}, Message: {message}")
        print(f"DEBUG: Session data: {session}")
        
        if state == 'initial':
            # Check if message contains leave intent
            if self.parse_leave_intent(message):
                # Try to extract details from the initial message
                details = self.extract_leave_details(message)
                session['leave_data'].update(details)
                
                print(f"DEBUG: Extracted details: {details}")
                
                # Check what information we still need
                missing_info = []
                if 'days' not in session['leave_data']:
                    missing_info.append('number of days')
                if 'reason' not in session['leave_data']:
                    missing_info.append('reason')
                
                if missing_info:
                    session['state'] = 'collecting_info'
                    session['missing_info'] = missing_info
                    print(f"DEBUG: Changed state to collecting_info")
                    return f"Hi {employee['name']}! I can help you apply for leave.\n\nI need the following information:\n• {chr(10).join(missing_info)}\n\nPlease provide the missing details."
                else:
                    # We have all info, proceed to confirmation
                    print(f"DEBUG: All info collected, going to confirmation")
                    return self.confirm_leave_details(session)
            else:
                return f"Hi {employee['name']}! I can help you apply for leave. Please tell me:\n• How many days do you need?\n• What's the reason?\n\nExample: 'I need 3 days leave for family emergency'\n\n(Type 'reset' to start over)"
        
        elif state == 'collecting_info':
            # Extract additional details
            new_details = self.extract_leave_details(message)
            session['leave_data'].update(new_details)
            
            print(f"DEBUG: Updated leave data: {session['leave_data']}")
            
            # Check if we have all required info
            if 'days' in session['leave_data'] and 'reason' in session['leave_data']:
                print(f"DEBUG: All info collected, going to confirmation")
                return self.confirm_leave_details(session)
            else:
                missing = []
                if 'days' not in session['leave_data']:
                    missing.append('number of days')
                if 'reason' not in session['leave_data']:
                    missing.append('reason')
                
                return f"I still need:\n• {chr(10).join(missing)}\n\nPlease provide the missing information."
        
        elif state == 'confirming':
            print(f"DEBUG: In confirming state, message: '{message.lower().strip()}'")
            if message.lower().strip() in ['yes', 'y', 'confirm', 'ok', 'proceed']:
                return self.submit_leave_request(session, phone)
            elif message.lower().strip() in ['no', 'n', 'cancel']:
                # Reset session
                del self.user_sessions[session_key]
                return "Leave application cancelled. Feel free to start again anytime!"
            else:
                return "Please reply with 'yes' to confirm or 'no' to cancel the leave application."
        
        return "I didn't understand. Please try again or type 'help' for assistance.\n\n(Type 'reset' to start over)"
    
    def confirm_leave_details(self, session: Dict) -> str:
        """Show leave details for confirmation"""
        leave_data = session['leave_data']
        employee = session['employee']
        
        confirmation_msg = f"""
📋 Leave Application Summary:

👤 Employee: {employee['name']}
📅 Days: {leave_data['days']} days
📝 Reason: {leave_data['reason']}
🏢 Department: {employee.get('department', 'N/A')}

Please reply 'YES' to confirm or 'NO' to cancel.
        """.strip()
        
        session['state'] = 'confirming'
        return confirmation_msg
    
    def submit_leave_request(self, session: Dict, phone: str) -> str:
        """Submit the leave request and notify manager"""
        leave_data = session['leave_data']
        employee = session['employee']
        
        print(f"DEBUG: Submitting leave request for {employee['name']}")
        
        # Submit to HR system
        result = self.hr_agent.submit_leave_request(
            teacher_name=employee['name'],
            leave_days=leave_data['days'],
            reason=leave_data['reason']
        )
        
        print(f"DEBUG: HR system result: {result}")
        
        if result['status'] == 'success':
            leave_id = result['leave_id']
            
            # Get AI analysis
            ai_analysis = self.hr_agent.get_ai_analysis(leave_id)
            
            # Notify manager
            manager_phone = self.get_manager_phone(employee)
            if manager_phone:
                manager_msg = f"""
🔔 New Leave Request #{leave_id}

👤 Employee: {employee['name']}
📞 Phone: {employee.get('phone', 'N/A')}
🏢 Department: {employee.get('department', 'N/A')}
📅 Days Requested: {leave_data['days']} days
📝 Reason: {leave_data['reason']}

🤖 AI Analysis Summary:
{ai_analysis.get('ai_analysis', 'Analysis not available')[:500]}...

Please review and approve/reject via the HR system.
                """.strip()
                
                self.send_whatsapp_message(manager_phone, manager_msg)
            
            # Clear session
            session_key = phone
            if session_key in self.user_sessions:
                del self.user_sessions[session_key]
                print(f"DEBUG: Cleared session for {phone}")
            
            return f"""
✅ Leave Request Submitted Successfully!

📋 Request ID: #{leave_id}
📅 Days: {leave_data['days']} days
📝 Reason: {leave_data['reason']}

Your manager has been notified and will review your request. You'll receive an update once it's processed.

Thank you! 🙏
            """.strip()
        
        else:
            return f"❌ Error submitting leave request: {result['message']}\n\nPlease try again or contact HR directly."

# Global instance to maintain session state across requests
whatsapp_agent_instance = None

# Flask webhook endpoint
@app.route('/webhook', methods=['POST', 'GET'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    global whatsapp_agent_instance
    
    # Use singleton pattern to maintain session state
    if whatsapp_agent_instance is None:
        whatsapp_agent_instance = WhatsAppHRAgent()
    
    whatsapp_agent = whatsapp_agent_instance
    
    print(f"Webhook called with method: {request.method}")
    print(f"Request data: {request.values}")
    
    if request.method == 'GET':
        # Handle Twilio webhook verification
        return "Webhook is working!", 200
    
    try:
        # Get message details
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        print(f"Incoming message: '{incoming_msg}' from {from_number}")
        
        # Extract phone number
        phone = whatsapp_agent.extract_phone_number(from_number)
        print(f"Extracted phone: {phone}")
        
        # Debug: Show current sessions
        print(f"DEBUG: Current sessions: {list(whatsapp_agent.user_sessions.keys())}")
        if phone in whatsapp_agent.user_sessions:
            print(f"DEBUG: Session for {phone}: {whatsapp_agent.user_sessions[phone]}")
        
        # Find employee
        employee = whatsapp_agent.find_employee_by_phone(phone)
        print(f"Found employee: {employee}")
        
        # Create response
        resp = MessagingResponse()
        
        if not employee:
            error_msg = "❌ Sorry, I couldn't find your employee record. Please contact HR directly or ensure you're messaging from your registered phone number."
            print(f"Employee not found, sending: {error_msg}")
            resp.message(error_msg)
        else:
            # Handle the conversation
            response_msg = whatsapp_agent.handle_leave_application(phone, incoming_msg, employee)
            print(f"Response message: {response_msg}")
            resp.message(response_msg)
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in webhook: {e}")
        import traceback
        traceback.print_exc()
        resp = MessagingResponse()
        resp.message("❌ Sorry, there was an error processing your request. Please try again.")
        return Response(str(resp), mimetype='text/xml')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == '__main__':
    # For development only
    print("🚀 Starting WhatsApp HR Agent...")
    print("📱 Webhook URL: http://localhost:5000/webhook")
    print("🌐 Make sure to expose this via ngrok for Twilio")
    app.run(debug=True, host='0.0.0.0', port=5000)