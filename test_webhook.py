"""
Test webhook locally to debug Twilio integration
"""
import requests
import json

def test_webhook_locally():
    """Test the webhook endpoint locally"""
    
    # Test data that mimics Twilio's request
    test_data = {
        'Body': 'I want to apply for leave',
        'From': 'whatsapp:+1234567890',  # Should match an employee in your Excel
        'To': 'whatsapp:+14155238886',
        'MessageSid': 'test_message_sid',
        'AccountSid': 'test_account_sid'
    }
    
    # Test the local webhook
    webhook_url = 'http://localhost:5000/webhook'
    
    print("🧪 Testing webhook locally...")
    print(f"📡 URL: {webhook_url}")
    print(f"📝 Data: {test_data}")
    
    try:
        # Test GET request first (webhook verification)
        print("\n1. Testing GET request (webhook verification)...")
        get_response = requests.get(webhook_url)
        print(f"   Status: {get_response.status_code}")
        print(f"   Response: {get_response.text}")
        
        # Test POST request (actual message)
        print("\n2. Testing POST request (message handling)...")
        post_response = requests.post(webhook_url, data=test_data)
        print(f"   Status: {post_response.status_code}")
        print(f"   Response: {post_response.text}")
        
        if post_response.status_code == 200:
            print("\n✅ Webhook is working correctly!")
        else:
            print(f"\n❌ Webhook returned status {post_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook. Make sure Flask app is running on port 5000")
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

def test_ngrok_webhook(ngrok_url):
    """Test the webhook through ngrok"""
    
    test_data = {
        'Body': 'I want to apply for leave',
        'From': 'whatsapp:+1234567890',
        'To': 'whatsapp:+14155238886',
        'MessageSid': 'test_message_sid',
        'AccountSid': 'test_account_sid'
    }
    
    webhook_url = f"{ngrok_url}/webhook"
    
    print(f"🌐 Testing ngrok webhook...")
    print(f"📡 URL: {webhook_url}")
    
    try:
        # Test GET request
        print("\n1. Testing GET request...")
        get_response = requests.get(webhook_url)
        print(f"   Status: {get_response.status_code}")
        print(f"   Response: {get_response.text}")
        
        # Test POST request
        print("\n2. Testing POST request...")
        post_response = requests.post(webhook_url, data=test_data)
        print(f"   Status: {post_response.status_code}")
        print(f"   Response: {post_response.text}")
        
        if post_response.status_code == 200:
            print("\n✅ Ngrok webhook is working!")
            print(f"🔗 Use this URL in Twilio: {webhook_url}")
        else:
            print(f"\n❌ Ngrok webhook returned status {post_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing ngrok webhook: {e}")

def main():
    print("🧪 Webhook Testing Tool")
    print("=" * 40)
    print("1. Test local webhook (localhost:5000)")
    print("2. Test ngrok webhook")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            test_webhook_locally()
        elif choice == '2':
            ngrok_url = input("Enter your ngrok URL (e.g., https://abc123.ngrok-free.dev): ").strip()
            if ngrok_url:
                test_ngrok_webhook(ngrok_url)
            else:
                print("❌ Please provide a valid ngrok URL")
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()