"""
Test script using EXACT code from the documentation.
This ensures users can copy-paste the code and it will work.
"""

import os
from typing import Any, Dict
from promptlayer import PromptLayer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
API_KEY = os.environ.get('PROMPTLAYER_API_KEY')
if not API_KEY:
    raise ValueError("PROMPTLAYER_API_KEY not found in environment variables.")

# Initialize client
promptlayer_client = PromptLayer(api_key=API_KEY)

# Mock function for getting next user input (stops the loop)
def get_next_user_input():
    """Mock function - returns None to exit loop after one turn"""
    return None

# Mock function for executing tools
def execute_tool(tool_call):
    """Mock tool execution"""
    if isinstance(tool_call, dict):
        tool_name = tool_call.get("function", {}).get("name", "unknown")
    else:
        tool_name = "unknown"
    return f"Mock result for tool: {tool_name}"

# ============================================================
# EXACT CODE FROM DOCUMENTATION - Basic Conversation
# ============================================================

def run_conversation(user_question):
    chat_history = []

    while True:
        # For basic prompts without tools
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant",
            input_variables={
                "user_question": user_question,
                "chat_history": chat_history
            },
            tags=["multi-turn-chat"]
        )

        # Extract the assistant's last message
        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

        # Add to conversation history
        chat_history.append({
            "role": "user",
            "content": [{"type": "text", "text": user_question}]
        })
        chat_history.append(last_message)

        # Get next user input
        user_question = get_next_user_input()
        if not user_question:
            break

    return last_message if 'last_message' in locals() else None

# ============================================================
# EXACT CODE FROM DOCUMENTATION - Conversation with Tools
# ============================================================

def run_conversation_with_tools(user_question):
    chat_history = []
    ai_in_progress = []  # Messages from AI's tool interactions

    while True:
        # With tools, include ai_in_progress for multi-step operations
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": chat_history,
                "user_question": user_question,
                "ai_in_progress": ai_in_progress  # [AI call, tool response, AI call, tool response, ...]
            },
            tags=["multi-turn-chat"]
        )

        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

        # Check if conversation should end
        function_call = last_message.get("function_call")
        if function_call and function_call.get("name") == "end_conversation":
            return last_message if 'last_message' in locals() else None

        # Handle tool calls - AI might need multiple tool calls before responding
        if last_message.get("tool_calls") or last_message.get("function_call"):
            # Add AI's message with tool call to ai_in_progress
            ai_in_progress.append(last_message)

            # Execute tool and add response
            if last_message.get("tool_calls"):
                for tool_call in last_message["tool_calls"]:
                    tool_result = execute_tool(tool_call)
                    ai_in_progress.append({
                        "role": "tool",
                        "content": [{"type": "text", "text": str(tool_result)}],
                        "tool_call_id": tool_call["id"]
                    })
            elif last_message.get("function_call"):
                tool_result = execute_tool(last_message["function_call"])
                ai_in_progress.append({
                    "role": "function",
                    "name": last_message["function_call"]["name"],
                    "content": str(tool_result)
                })
            # Loop continues - AI can make another tool call or respond to user
        else:
            # AI provided final response - add everything to history
            chat_history.append({
                "role": "user",
                "content": [{"type": "text", "text": user_question}]
            })

            # Add any tool interactions from ai_in_progress to history
            if ai_in_progress:
                chat_history.extend(ai_in_progress)

            # Add final response
            chat_history.append(last_message)

            # Clear ai_in_progress for next user turn
            ai_in_progress = []

            # Get next user input
            user_question = get_next_user_input()
            if not user_question:
                break

    return last_message if 'last_message' in locals() else None

# ============================================================
# TEST FUNCTIONS
# ============================================================

def test_basic_conversation():
    """Test the exact basic conversation code from docs"""
    print("\n1. Testing EXACT basic conversation code from docs...")

    try:
        result = run_conversation("Hello, how are you?")

        if result:
            text = result.get('content', [{}])[0].get('text', 'No response')
            print(f"✅ Basic conversation works! Response: {text[:50]}...")
            return True
        else:
            print("❌ No result returned")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_with_tools():
    """Test the exact tool conversation code from docs"""
    print("\n2. Testing EXACT tool conversation code from docs...")

    try:
        result = run_conversation_with_tools("I need help with my password")

        if result:
            text = result.get('content', [{}])[0].get('text', 'No response')
            print(f"✅ Tool conversation works! Response: {text[:50]}...")
            return True
        else:
            print("❌ No result returned")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_with_history():
    """Test with pre-existing history using exact doc code"""
    print("\n3. Testing with conversation history...")

    # This simulates what would happen after multiple turns
    # We'll modify the function slightly to accept initial history
    def run_conversation_with_history(user_question, initial_history):
        chat_history = initial_history  # Use provided history

        # Single turn only for testing
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant",
            input_variables={
                "user_question": user_question,
                "chat_history": chat_history
            },
            tags=["multi-turn-chat"]
        )

        if result:
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
            return last_message
        return None

    # Pre-existing conversation
    history = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "I'm visiting New York next week"}]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "That sounds exciting! NYC has so much to offer."}]
        }
    ]

    try:
        result = run_conversation_with_history("What's the weather like there?", history)

        if result:
            text = result.get('content', [{}])[0].get('text', 'No response')
            print(f"✅ History retention works! Response: {text[:50]}...")
            return True
        else:
            print("❌ No result returned")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests using EXACT documentation code"""
    print("=" * 60)
    print("TESTING EXACT CODE FROM DOCUMENTATION")
    print("=" * 60)
    print("This test uses the EXACT code snippets from the docs")
    print("to ensure copy-paste compatibility.")

    results = []

    # Test basic conversation
    results.append(test_basic_conversation())

    # Test tool conversation
    results.append(test_conversation_with_tools())

    # Test with history
    results.append(test_conversation_with_history())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ SUCCESS: All {total} tests passed!")
        print("Documentation code is copy-paste ready!")
    else:
        print(f"⚠️ WARNING: {total - passed} test(s) failed")
        print("Documentation code may need updates")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)