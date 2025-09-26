# Testing Instructions for Documentation Examples

This document provides instructions for testing code examples in the PromptLayer documentation.

## Test Workspace

We maintain a dedicated test workspace for documentation examples with pre-configured prompts and settings.

### Workspace Details
- **Purpose**: Testing documentation code examples
- **API Key**: Available in secure storage (not committed to repo)
- **Workspace ID**: Contact team for access

## Testing Multi-Turn Chat Examples

### Required Prompts

To test the multi-turn chat examples from the documentation, you only need TWO prompts set up in your workspace:

1. **multi-turn-assistant**
   - Type: Chat prompt template
   - Required placeholders:
     - `{{chat_history}}` - Message placeholder for conversation history
     - `{{user_question}}` - Text variable for current user input
     - `{{ai_in_progress}}` - Array variable for tool call tracking (can be empty list if not using tools)
   - Example system message: "You are a helpful assistant. Use the conversation history to maintain context."
   - Used for: Basic multi-turn conversations, context retention tests, and examples without tools

2. **multi-turn-assistant-with-tools** (Optional - only if testing tool functionality)
   - Type: Chat prompt template
   - Required placeholders (in this order):
     - `{{chat_history}}` - Message placeholder for conversation history
     - `{{user_question}}` - Text variable for current user input
     - `{{ai_in_progress}}` - Message placeholder for tool interaction messages (MUST come AFTER user_question)
     - `{{user_context}}` - Object variable for additional context (optional)
   - Important: The order matters! `ai_in_progress` must come after `user_question` because it contains the AI's tool interactions in response to the user's question
   - Tool definitions (if testing tools):
     - `search_kb` - Search knowledge base
     - `create_ticket` - Create support ticket
     - `escalate` - Escalate to human agent
     - `end_conversation` - End the conversation
   - Used for: Examples demonstrating tool usage in multi-turn conversations

### Running Tests

1. Install dependencies:
```bash
pip install promptlayer python-dotenv
```

2. Set your API key:
   - Copy `.env.example` to `.env`
   - Add your PromptLayer API key to the `.env` file:
   ```
   PROMPTLAYER_API_KEY=your_api_key_here
   ```

3. Run the test scripts:
```bash
# Run all basic tests
python testing/test_multi_turn_chat.py

# Run simplified sanity checks
python testing/test_multi_turn_chat_simple.py

# Run multi-turn conversation loop test (3+ turns)
python testing/test_multi_turn_loop.py

# Run tool conversation test
python testing/test_multi_turn_with_tools.py

# Debug tool interactions
python testing/test_tool_debug.py
```

### Test Script Locations

All test scripts are located in the `testing/` folder:

- **`test_multi_turn_chat.py`** - Main test suite with all examples from documentation
- **`test_multi_turn_chat_simple.py`** - Quick sanity checks without loops
- **`test_multi_turn_loop.py`** - Tests multiple conversation turns (3+) with context retention
- **`test_multi_turn_with_tools.py`** - Demonstrates proper tool handling with ai_in_progress
- **`test_tool_debug.py`** - Debug script to understand tool conversation flow

## Adding New Test Prompts

When adding new documentation examples that require testing:

1. Create the prompt template in the test workspace
2. Document the required placeholders and configuration here
3. Add corresponding test cases to the test script
4. Verify all examples work before publishing documentation

## Troubleshooting

### Common Issues

1. **Missing placeholders**: Ensure all required placeholders are defined in your prompt template
2. **API key errors**: Verify your API key has access to the test workspace
3. **Tool call errors**: Check that tool definitions match the expected format in the documentation

### Debug Mode

Enable debug output by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contact

For access to the test workspace or assistance with testing, contact the PromptLayer team.