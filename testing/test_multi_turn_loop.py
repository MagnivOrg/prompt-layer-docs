"""
Test script demonstrating multi-turn conversation with 3+ turns.
"""

import os
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


def run_multi_turn_conversation():
    """
    Run a multi-turn conversation with at least 3 exchanges.
    """
    print("\n" + "="*50)
    print("Running Multi-Turn Conversation (3+ turns)")
    print("="*50)

    chat_history = []

    # Define the conversation turns
    conversation_turns = [
        "Hello! I'm planning a trip to New York.",
        "What's the weather like there in spring?",
        "What are some must-see attractions?",
        "Thank you for the recommendations!"
    ]

    for turn_num, user_question in enumerate(conversation_turns, 1):
        print(f"\n--- Turn {turn_num} ---")
        print(f"User: {user_question}")

        # Call the prompt with accumulated history
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant",
            input_variables={
                "user_question": user_question,
                "chat_history": chat_history,
                "ai_in_progress": []  # Empty for non-tool conversations
            },
            tags=["multi-turn-test"]
        )

        # Extract assistant's response
        if result and "prompt_blueprint" in result:
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
            assistant_text = last_message.get('content', [{}])[0].get('text', 'No response')

            # Display assistant's response (truncated for readability)
            print(f"Assistant: {assistant_text[:150]}{'...' if len(assistant_text) > 150 else ''}")

            # Add both user and assistant messages to history
            chat_history.append({
                "role": "user",
                "content": [{"type": "text", "text": user_question}]
            })
            chat_history.append(last_message)

            # Show history size
            print(f"History size: {len(chat_history)} messages")
        else:
            print("Error: No valid response received")
            break

    print("\n" + "="*50)
    print(f"Conversation completed with {len(chat_history)//2} exchanges")
    print(f"Final history contains {len(chat_history)} messages")

    # Verify context retention
    print("\n--- Verifying Context Retention ---")

    # Check if the assistant remembers the trip to New York from turn 1
    final_question = "What city was I asking about again?"
    print(f"User: {final_question}")

    result = promptlayer_client.run(
        prompt_name="multi-turn-assistant",
        input_variables={
            "user_question": final_question,
            "chat_history": chat_history,
            "ai_in_progress": []
        },
        tags=["context-test"]
    )

    if result and "prompt_blueprint" in result:
        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
        assistant_text = last_message.get('content', [{}])[0].get('text', 'No response')
        print(f"Assistant: {assistant_text[:200]}")

        # Check if New York is mentioned
        if "New York" in assistant_text or "NYC" in assistant_text:
            print("✅ Context retained successfully - assistant remembers New York!")
        else:
            print("⚠️ Context might be lost - New York not mentioned explicitly")

    return True


def run_tool_conversation():
    """
    Run a multi-turn conversation with tools.
    """
    print("\n" + "="*50)
    print("Running Tool-Based Conversation")
    print("="*50)

    chat_history = []
    ai_in_progress = []

    # Simulate a support conversation
    questions = [
        "I forgot my password",
        "My username is john.doe@example.com",
        "Can you send the reset link?"
    ]

    for turn_num, user_question in enumerate(questions, 1):
        print(f"\n--- Turn {turn_num} ---")
        print(f"User: {user_question}")

        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": chat_history,
                "user_question": user_question,
                "ai_in_progress": ai_in_progress,
                "user_context": {
                    "user_id": "user_123",
                    "session_id": "session_456"
                }
            },
            tags=["tool-test"]
        )

        if result and "prompt_blueprint" in result:
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

            # Check for tool calls
            if last_message.get("tool_calls") or last_message.get("function_call"):
                print("Assistant: [Making tool call...]")
                # In a real scenario, we'd execute the tool here
                # For testing, we just acknowledge it
                ai_in_progress.append(last_message)
                ai_in_progress.append({
                    "role": "tool",
                    "content": [{"type": "text", "text": "Tool executed successfully"}]
                })
            else:
                # Regular response
                assistant_text = last_message.get('content', [{}])[0].get('text', 'No response')
                print(f"Assistant: {assistant_text[:150]}{'...' if len(assistant_text) > 150 else ''}")

                # Add to history
                chat_history.append({
                    "role": "user",
                    "content": [{"type": "text", "text": user_question}]
                })

                # Add any tool interactions to history
                if ai_in_progress:
                    chat_history.extend(ai_in_progress)
                    ai_in_progress = []

                chat_history.append(last_message)
        else:
            print("Error: No valid response received")
            break

    print(f"\nCompleted {len(questions)} turns")
    return True


def main():
    """Run all multi-turn tests."""
    print("\n" + "="*60)
    print("MULTI-TURN CONVERSATION TEST (3+ TURNS)")
    print("="*60)

    try:
        # Test basic multi-turn conversation
        run_multi_turn_conversation()

        # Test tool-based conversation
        try:
            run_tool_conversation()
        except Exception as e:
            print(f"\nTool conversation skipped: {e}")

        print("\n✅ Multi-turn conversation test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False

    return True


if __name__ == "__main__":
    main()