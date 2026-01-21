"""
Debug reason extraction for specific message
"""
import re

def debug_extract_leave_details(message: str):
    """Debug version of extract_leave_details"""
    details = {}
    message_lower = message.lower().strip()
    
    print(f"🔍 Debugging message: '{message}'")
    print(f"🔍 Lowercase: '{message_lower}'")
    
    # Enhanced reason extraction patterns
    reason_patterns = [
        # Common prepositions
        r'for\s+(.+?)(?:\.|$|because|due to|since)',
        r'because\s+(.+?)(?:\.|$|for|due to)',
        r'due to\s+(.+?)(?:\.|$|because|for)',
        r'since\s+(.+?)(?:\.|$|because|for)',
        r'as\s+(.+?)(?:\.|$|because|for)',
        r'to\s+(.+?)(?:\.|$|because|for|due to)',  # Added "to" pattern
        
        # Reason indicators
        r'reason:?\s*(.+?)(?:\.|$)',
        r'purpose:?\s*(.+?)(?:\.|$)',
        
        # Medical/personal reasons (standalone)
        r'(sick|ill|unwell|not feeling well)',
        r'(doctor|hospital|medical|appointment)',
        r'(family|personal|emergency)',
        r'(vacation|holiday|travel|trip)',
        r'(wedding|marriage|funeral)',
        r'(pregnant|pregnancy|maternity|paternity)',
        r'(business|conference|meeting|training)',  # Added business reasons
        
        # Contextual extraction - more comprehensive
        r'i\s+(am|will be|have to|need to|must)\s+(.+?)(?:\.|$)',
        r'my\s+(.+?)(?:\.|$)',
        r'going\s+(.+?)(?:\.|$)',
        r'attending\s+(.+?)(?:\.|$)',  # Added attending pattern
        
        # Catch-all for "off" constructions
        r'off\s+(.+?)(?:\.|$)',
        r'leave\s+(.+?)(?:\.|$)',
    ]
    
    print(f"\n📋 Testing {len(reason_patterns)} patterns:")
    
    for i, pattern in enumerate(reason_patterns, 1):
        match = re.search(pattern, message_lower)
        if match:
            raw_reason = match.group(1).strip()
            
            # Clean up the reason
            cleaned_reason = re.sub(r'^(to|for|because|due to|since|as)\s+', '', raw_reason)
            cleaned_reason = re.sub(r'\s+', ' ', cleaned_reason)  # Remove extra spaces
            
            print(f"  {i:2d}. Pattern: {pattern}")
            print(f"      ✅ MATCH: '{raw_reason}' → '{cleaned_reason}'")
            
            # Skip very short or generic reasons
            if len(cleaned_reason) > 2 and cleaned_reason not in ['it', 'this', 'that', 'some', 'the']:
                details['reason'] = cleaned_reason
                print(f"      ✅ ACCEPTED: '{cleaned_reason}'")
                break
            else:
                print(f"      ❌ REJECTED: Too short or generic")
        else:
            print(f"  {i:2d}. Pattern: {pattern} → ❌ No match")
    
    return details

def test_problematic_messages():
    """Test messages that are having issues"""
    
    test_messages = [
        "I need a week off to attend a business party",
        "to attend a business party",  # Follow-up message
        "I want 3 days leave for vacation",
        "Need time off to go to wedding",
        "I need leave to visit family",
        "Want 2 days off for personal reasons",
    ]
    
    print("🧪 Testing Reason Extraction")
    print("=" * 60)
    
    for message in test_messages:
        print(f"\n{'='*60}")
        details = debug_extract_leave_details(message)
        
        print(f"\n🎯 Final Result:")
        if 'reason' in details:
            print(f"   Reason: '{details['reason']}' ✅")
        else:
            print(f"   Reason: Not found ❌")

if __name__ == "__main__":
    test_problematic_messages()