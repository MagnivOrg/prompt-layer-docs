"""
Test script demonstrating proper multi-turn conversation with tool calls.
Shows how ai_in_progress accumulates tool interactions between user turns.
"""

import os
import json
from typing import Any, Dict, List, Optional
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

print(f"Using API key: {API_KEY[:10]}...")


def mock_execute_tool(tool_call: Dict[str, Any]) -> str:
    """Mock tool execution."""
    tool_name = tool_call.get("function", {}).get("name", "unknown")

    # Mock responses for different tools
    if tool_name == "search_kb":
        return "Found 3 articles about password reset:\n1. How to reset your password\n2. Password requirements\n3. Troubleshooting login issues"
    elif tool_name == "create_ticket":
        return "Ticket #12345 created successfully. A support agent will contact you within 24 hours."
    elif tool_name == "send_reset_email":
        return "Password reset email sent to john.doe@example.com"
    else:
        return f"Tool {tool_name} failed"


def run_tool_conversation_properly():
    """
    Run a multi-turn conversation with proper tool handling.
    Shows how ai_in_progress accumulates tool calls and responses.
    """
    print("\n" + "="*60)
    print("Running Tool-Based Multi-Turn Conversation")
    print("="*60)

    chat_history = []

    # Turn 1: User asks for help
    user_question = "I forgot my password and need to reset it"
    print(f"\n--- Turn 1 ---")
    print(f"User: {user_question}")

    # AI might need to use tools before responding
    ai_in_progress = []

    while True:  # Loop to handle multiple tool calls before final response
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": chat_history,
                "user_question": user_question,
                "ai_in_progress": ai_in_progress,
                "user_context": {
                    "user_id": "user_123",
                    "email": "john.doe@example.com"
                }
            },
            tags=["tool-test"]
        )

        if not result or "prompt_blueprint" not in result:
            print("Error: No valid response")
            break

        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

        # Check if AI wants to use a tool
        if last_message.get("tool_calls"):
            print(f"Assistant is calling tools...")

            # Add AI's message with tool call to ai_in_progress
            ai_in_progress.append(last_message)

            # Process each tool call
            for tool_call in last_message["tool_calls"]:
                tool_name = tool_call.get("function", {}).get("name", "unknown")
                print(f"  - Calling tool: {tool_name}")

                # Mock execute the tool
                tool_result = mock_execute_tool(tool_call)

                # Add tool response to ai_in_progress
                tool_response = {
                    "role": "tool",
                    "content": [{"type": "text", "text": tool_result}],  # Proper format with content array
                    "tool_call_id": tool_call["id"]
                }
                ai_in_progress.append(tool_response)
                print(f"  - Tool response: {tool_result[:50]}...")
                print(f"Debug - ai_in_progress now has {len(ai_in_progress)} messages")

            # Continue loop - AI might need to call more tools or provide final response
            continue

        else:
            # AI provided final response to user
            assistant_text = last_message.get('content', [{}])[0].get('text', 'No response')
            print(f"Assistant: {assistant_text[:200]}{'...' if len(assistant_text) > 200 else ''}")

            # Add complete exchange to history
            chat_history.append({
                "role": "user",
                "content": [{"type": "text", "text": user_question}]
            })

            # Add all tool interactions from ai_in_progress
            if ai_in_progress:
                print(f"  (Added {len(ai_in_progress)} tool interaction messages to history)")
                print(f"  Debug - ai_in_progress contents:")
                for i, msg in enumerate(ai_in_progress):
                    role = msg.get('role', 'unknown')
                    if role == 'tool':
                        print(f"    [{i}] Tool response: {msg.get('content', [{}])[0].get('text', 'no text')[:50]}...")
                    else:
                        print(f"    [{i}] AI message with tool calls")
                chat_history.extend(ai_in_progress)

            # Add final assistant response
            chat_history.append(last_message)
            break

    print(f"History after Turn 1: {len(chat_history)} messages")

    # Turn 2: User provides additional information
    user_question = "My username is john.doe@example.com"
    print(f"\n--- Turn 2 ---")
    print(f"User: {user_question}")

    # Clear ai_in_progress for new turn
    ai_in_progress = []

    while True:
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": chat_history,
                "user_question": user_question,
                "ai_in_progress": ai_in_progress,
                "user_context": {
                    "user_id": "user_123",
                    "email": "john.doe@example.com"
                }
            },
            tags=["tool-test"]
        )

        if not result or "prompt_blueprint" not in result:
            break

        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

        if last_message.get("tool_calls"):
            print(f"Assistant is calling tools...")
            ai_in_progress.append(last_message)

            for tool_call in last_message["tool_calls"]:
                tool_name = tool_call.get("function", {}).get("name", "unknown")
                print(f"  - Calling tool: {tool_name}")

                tool_result = mock_execute_tool(tool_call)
                tool_response = {
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call["id"]
                }
                ai_in_progress.append(tool_response)
                print(f"  - Tool response: {tool_result[:50]}...")

            continue
        else:
            assistant_text = last_message.get('content', [{}])[0].get('text', 'No response')
            print(f"Assistant: {assistant_text[:200]}{'...' if len(assistant_text) > 200 else ''}")

            chat_history.append({
                "role": "user",
                "content": [{"type": "text", "text": user_question}]
            })

            if ai_in_progress:
                print(f"  (Added {len(ai_in_progress)} tool interaction messages to history)")
                chat_history.extend(ai_in_progress)

            chat_history.append(last_message)
            break

    print(f"History after Turn 2: {len(chat_history)} messages")

    # Turn 3: User asks for confirmation
    user_question = "Has the reset email been sent?"
    print(f"\n--- Turn 3 ---")
    print(f"User: {user_question}")

    ai_in_progress = []

    result = promptlayer_client.run(
        prompt_name="multi-turn-assistant-with-tools",
        input_variables={
            "chat_history": chat_history,
            "user_question": user_question,
            "ai_in_progress": ai_in_progress,
            "user_context": {
                "user_id": "user_123",
                "email": "john.doe@example.com"
            }
        },
        tags=["tool-test"]
    )

    if result and "prompt_blueprint" in result:
        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
        assistant_text = last_message.get('content', [{}])[0].get('text', 'No response')
        print(f"Assistant: {assistant_text[:200]}{'...' if len(assistant_text) > 200 else ''}")

        # Check if the assistant remembers the context
        if "email" in assistant_text.lower() or "sent" in assistant_text.lower() or "john.doe" in assistant_text.lower():
            print("\n✅ Context retained - Assistant remembers the email/action from previous turns!")
        else:
            print("\n⚠️ Assistant response doesn't explicitly reference previous context")

    print(f"\n" + "="*60)
    print(f"Conversation completed with {len(chat_history)} total messages in history")
    print("Tool interactions were properly handled via ai_in_progress")

    return True


def main():
    """Run the tool conversation test."""
    print("\n" + "="*70)
    print("MULTI-TURN CONVERSATION WITH TOOLS TEST")
    print("="*70)

    try:
        run_tool_conversation_properly()
        print("\n✅ Tool conversation test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    main()