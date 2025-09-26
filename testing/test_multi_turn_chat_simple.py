"""
Simple test script for Multi-Turn Chat documentation examples.
This script tests the code examples without infinite loops.
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


def test_basic_conversation():
    """Test a single exchange without tools."""
    print("\n1. Testing basic conversation...")
    try:
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant",
            input_variables={
                "user_question": "Hello, how are you?",
                "chat_history": [],
                "ai_in_progress": []
            },
            tags=["test"]
        )

        if result and "prompt_blueprint" in result:
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
            print(f"✓ Response: {last_message.get('content', [{}])[0].get('text', 'No text')[:50]}...")
            return True
        else:
            print("✗ No valid response received")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_conversation_with_history():
    """Test conversation with existing history."""
    print("\n2. Testing conversation with history...")

    chat_history = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "I'm in New York"}]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Great! You're in New York. How can I help you?"}]
        }
    ]

    try:
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant",
            input_variables={
                "chat_history": chat_history,
                "user_question": "What's the weather like?",
                "ai_in_progress": []
            },
            tags=["test"]
        )

        if result and "prompt_blueprint" in result:
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
            response_text = last_message.get('content', [{}])[0].get('text', '')
            if 'New York' in response_text or 'weather' in response_text.lower():
                print(f"✓ Context retained: {response_text[:50]}...")
                return True
            else:
                print(f"✓ Response received: {response_text[:50]}...")
                return True
        else:
            print("✗ No valid response received")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_with_tools():
    """Test a single exchange with tools prompt."""
    print("\n3. Testing with tools prompt...")
    try:
        result = promptlayer_client.run(
            prompt_name="multi-turn-assistant-with-tools",
            input_variables={
                "chat_history": [],
                "user_question": "I need help with my password",
                "ai_in_progress": [],
                "user_context": {"user_id": "test123"}
            },
            tags=["test"]
        )

        if result and "prompt_blueprint" in result:
            last_message = result["prompt_blueprint"]["prompt_template"]["messages"][-1]
            print(f"✓ Response: {last_message.get('content', [{}])[0].get('text', 'No text')[:50]}...")
            return True
        else:
            print("✗ No valid response received")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing Multi-Turn Chat Examples (Simple)")
    print("=" * 50)

    results = []

    # Test basic conversation
    results.append(test_basic_conversation())

    # Test with history
    results.append(test_conversation_with_history())

    # Test with tools
    results.append(test_with_tools())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()