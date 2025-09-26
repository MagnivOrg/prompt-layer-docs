"""
Test script for Multi-Turn Chat documentation examples.
This script tests the code examples from the Multi-Turn Chat documentation page.

Prerequisites:
1. Set PROMPTLAYER_API_KEY environment variable
2. Create the following prompts in your PromptLayer workspace:
   - "multi-turn-assistant" (basic chat)
   - "multi-turn-assistant-with-tools" (chat with tools)

See TESTING_INSTRUCTIONS.md for detailed setup instructions.
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
    raise ValueError("PROMPTLAYER_API_KEY not found in environment variables. Please set it in .env file.")

# Initialize client
promptlayer_client = PromptLayer(api_key=API_KEY)

print(f"Using API key: {API_KEY[:10]}...")
print(f"PromptLayer version: {promptlayer_client.__class__.__module__}")


def execute_tool(tool_call: Dict[str, Any]) -> Any:
    """Mock tool execution for testing."""
    tool_name = tool_call.get("function", {}).get("name", "")

    if tool_name == "search_kb":
        return {"results": ["Article about password reset", "FAQ about billing"]}
    elif tool_name == "create_ticket":
        return {"ticket_id": "TICKET-12345", "status": "created"}
    elif tool_name == "escalate":
        return {"escalated": True, "agent": "human_support"}
    elif tool_name == "get_weather":
        return {"temperature": "72°F", "conditions": "sunny"}
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def get_next_user_input() -> Optional[str]:
    """Get next user input - for testing, we'll return None to end conversation."""
    return None  # End conversation after first exchange


def run_conversation(user_question: str) -> Dict[str, Any]:
    """
    Main conversation loop from the documentation.
    This is the exact code from the Implementation Pattern section.
    """
    chat_history = []

    while True:
        # For basic prompts without tools
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant",
            input_variables={
                "user_question": user_question,
                "chat_history": chat_history or [],
                "ai_in_progress": []  # Default to empty list
            },
            tags=["multi-turn-chat"]
        )

        # Extract the assistant's last message
        last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

        # Check if conversation should end
        function_call = last_message.get("function_call")
        if function_call and function_call.get("name") == "end_conversation":
            return last_message if 'last_message' in locals() else None

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


def run_conversation_with_tools(user_question: str) -> Dict[str, Any]:
    """
    Conversation loop with tool support from the documentation.
    This demonstrates proper ai_in_progress usage for tool interactions.
    """
    chat_history = []
    ai_in_progress = []  # Messages from AI's tool interactions

    while True:
        # With tools, include ai_in_progress for multi-step operations
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": chat_history or [],
                "user_question": user_question,
                "ai_in_progress": ai_in_progress or []  # [AI call, tool response, AI call, tool response, ...]
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


def test_context_retention():
    """
    Test function from the documentation.
    Tests how the assistant retains context from conversation history.
    """
    test_history = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "I'm in New York"}]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Got it, you're in New York. How can I help you?"}]
        }
    ]

    result = promptlayer_client.run(
        prompt_name="multi-turn-assistant",
        input_variables={
            "chat_history": test_history,
            "user_question": "What's the weather like?",
            "ai_in_progress": []  # Default to empty list
        }
    )

    last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
    # Assistant should reference New York from context
    assert "New York" in last_message["content"][0]["text"]
    print("✓ Context retention test passed")
    return last_message if 'last_message' in locals() else None


def test_message_placeholder_example():
    """Test the message placeholder example from the documentation."""
    result = promptlayer_client.run(
        prompt_name="multi-turn-assistant",
        input_variables={
            "chat_history": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "What's the weather?"}]
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "I'll check the weather for you."}]
                }
            ],
            "user_question": "How about tomorrow?",
            "ai_in_progress": []  # Default to empty list
        }
    )

    print("✓ Message placeholder example executed successfully")
    return result


class StatelessToolAgent:
    """Tool-Enabled Assistant example from the documentation."""

    def __init__(self, promptlayer_client):
        self.client = promptlayer_client
        self.max_turns = 20

    def get_user_context(self) -> Dict[str, Any]:
        """Mock user context for testing."""
        return {
            "user_id": "user_123",
            "account_type": "premium",
            "previous_tickets": 2
        }

    def get_next_user_input(self) -> Optional[str]:
        """For testing, return None to end conversation."""
        return None

    def execute_tool(self, tool_call: Dict[str, Any]) -> Any:
        """Execute tools for support agent."""
        return execute_tool(tool_call)

    def format_final_response(self, last_message: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final response."""
        return {
            "status": "conversation_ended",
            "final_message": last_message
        }

    def handle_max_turns_reached(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle case when max turns is reached."""
        return {
            "status": "max_turns_reached",
            "history_length": len(chat_history)
        }

    def run_conversation(self, initial_question: str) -> Dict[str, Any]:
        """
        Run the support conversation.
        This is the exact code from the Example section.
        """
        chat_history = []
        ai_in_progress = []
        user_question = initial_question
        turn_count = 0

        while turn_count < self.max_turns:
            # Run stateless turn
            result = self.client.run(
                prompt_name="multi-turn-assistant-with-tools",
                input_variables={
                    "chat_history": chat_history or [],
                    "user_question": user_question,
                    "ai_in_progress": ai_in_progress or [],  # After user_question, contains tool interactions
                    "user_context": self.get_user_context()
                },
                tags=["support", "multi-turn"]
            )

            # Extract assistant's response
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

            # Check for conversation end
            if last_message.get("function_call", {}).get("name") == "end_conversation":
                return self.format_final_response(last_message)

            # Handle tool calls
            if last_message.get("tool_calls"):
                tool_results = []
                for tool_call in last_message["tool_calls"]:
                    tool_result = self.execute_tool(tool_call)
                    tool_results.append({
                        "tool": tool_call["function"]["name"],
                        "result": tool_result
                    })
                ai_in_progress.extend(tool_results)
            else:
                # Add messages to history
                chat_history.append({
                    "role": "user",
                    "content": [{"type": "text", "text": user_question}]
                })
                chat_history.append(last_message)

                # Get next user input
                user_question = self.get_next_user_input()
                if not user_question:
                    break

                # Clear ai_in_progress for next turn
                ai_in_progress = []

            turn_count += 1

        return self.handle_max_turns_reached(chat_history)


def test_simple_run():
    """Test that the PromptLayer client is working."""
    try:
        # This should work even without specific prompts
        print("Testing PromptLayer client initialization...")
        pl = PromptLayer(api_key=API_KEY)
        print("✓ Client initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Client initialization failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Multi-Turn Chat Documentation Examples")
    print("=" * 50)

    print("\n0. Testing PromptLayer client...")
    if not test_simple_run():
        print("\n⚠️  Client initialization failed. Check your API key.")
        print("Set PROMPTLAYER_API_KEY environment variable or update the script.")
        return

    print("\n1. Testing basic conversation loop...")
    try:
        result = run_conversation("Hello, how can you help me?")
        print("✓ Basic conversation executed successfully")
    except Exception as e:
        print(f"✗ Basic conversation failed: {e}")

    print("\n2. Testing context retention...")
    try:
        test_context_retention()
    except Exception as e:
        print(f"✗ Context retention test failed: {e}")

    print("\n3. Testing message placeholder example...")
    try:
        test_message_placeholder_example()
    except Exception as e:
        print(f"✗ Message placeholder test failed: {e}")

    print("\n4. Testing conversation with tools...")
    try:
        result = run_conversation_with_tools("I need help resetting my password")
        print("✓ Conversation with tools executed successfully")
    except Exception as e:
        print(f"✗ Conversation with tools test failed: {e}")

    print("\n5. Testing tool-enabled assistant class...")
    try:
        agent = StatelessToolAgent(promptlayer_client)
        result = agent.run_conversation("I need help with my account")
        print("✓ Tool-enabled assistant class executed successfully")
    except Exception as e:
        print(f"✗ Tool-enabled assistant class test failed: {e}")

    print("\n" + "=" * 50)
    print("Testing complete!")


if __name__ == "__main__":
    main()