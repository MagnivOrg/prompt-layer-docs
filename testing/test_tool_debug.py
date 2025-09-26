"""
Debug script to understand tool conversation flow.
"""

import os
import json
from promptlayer import PromptLayer
from dotenv import load_dotenv

load_dotenv()
client = PromptLayer(api_key=os.environ.get('PROMPTLAYER_API_KEY'))

print("Testing Tool Conversation Flow")
print("=" * 60)

chat_history = []
ai_in_progress = []
user_question = "I forgot my password and need to reset it"

print(f"\nUser: {user_question}")
print("\n--- First API Call (no tools yet) ---")

# First call - should trigger tool call
result = client.run(
    prompt_name="multi-turn-assistant-with-tools",
    input_variables={
        "chat_history": chat_history,
        "user_question": user_question,
        "ai_in_progress": ai_in_progress,
        "user_context": {"user_id": "test123"}
    }
)

if result:
    last_msg = result["prompt_blueprint"]["prompt_template"]["messages"][-1]

    if last_msg.get("tool_calls"):
        print(f"AI wants to call {len(last_msg['tool_calls'])} tool(s)")

        # Add AI's message to ai_in_progress
        ai_in_progress.append(last_msg)
        print(f"Added AI message to ai_in_progress (length: {len(ai_in_progress)})")

        # Add tool responses
        for tool_call in last_msg["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            print(f"  Tool: {tool_name}")

            # Create tool response
            tool_response = {
                "role": "tool",
                "content": [{"type": "text", "text": f"Tool {tool_name} executed: Found password reset instructions"}],
                "tool_call_id": tool_call["id"]
            }
            ai_in_progress.append(tool_response)
            print(f"  Added tool response (ai_in_progress length: {len(ai_in_progress)})")

        print(f"\n--- Second API Call (with tool responses) ---")
        print(f"ai_in_progress contains {len(ai_in_progress)} messages:")
        for i, msg in enumerate(ai_in_progress):
            role = msg.get("role")
            if role == "tool":
                content = msg.get("content", [{}])[0].get("text", "")[:50]
                print(f"  [{i}] tool: {content}...")
            else:
                print(f"  [{i}] assistant: (message with tool calls)")

        # Second call with tool responses
        print("\nCalling API with tool responses...")
        result2 = client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": chat_history,
                "user_question": user_question,
                "ai_in_progress": ai_in_progress,
                "user_context": {"user_id": "test123"}
            }
        )

        if result2:
            last_msg2 = result2["prompt_blueprint"]["prompt_template"]["messages"][-1]

            if last_msg2.get("tool_calls"):
                print(f"AI wants to call MORE tools: {[tc['function']['name'] for tc in last_msg2['tool_calls']]}")
                print("(This might mean the prompt isn't seeing the tool responses)")
            else:
                print("AI provided final response:")
                text = last_msg2.get("content", [{}])[0].get("text", "")
                print(f"  {text[:200]}...")
    else:
        print("AI didn't call any tools")
        text = last_msg.get("content", [{}])[0].get("text", "")
        print(f"Response: {text[:200]}...")

print("\n" + "=" * 60)
print("Conclusion:")
print("If the AI keeps calling tools, the prompt may not have the ai_in_progress placeholder")
print("or it's not configured to accept tool responses in the expected format.")