# Testing Suite for PromptLayer Documentation

This folder contains test scripts for validating code examples in the PromptLayer documentation.

## Quick Start

1. Ensure you have `.env` configured in the parent directory with:
   ```
   PROMPTLAYER_API_KEY=your_api_key_here
   OPENAI_API_KEY=your_openai_key_here  # If using OpenAI models
   ANTHROPIC_API_KEY=your_anthropic_key_here  # If using Anthropic models
   ```

2. Install dependencies:
   ```bash
   pip install promptlayer python-dotenv
   ```

3. Run tests:
   ```bash
   python testing/test_multi_turn_chat_simple.py  # Quick sanity check
   ```

## Test Files

### Core Tests
- **`test_multi_turn_chat.py`** - Complete test suite from documentation examples
- **`test_multi_turn_chat_simple.py`** - Quick validation without loops

### Advanced Tests
- **`test_multi_turn_loop.py`** - Multi-turn conversation with 3+ exchanges
- **`test_multi_turn_with_tools.py`** - Tool handling with ai_in_progress
- **`test_tool_debug.py`** - Debug tool conversation flow

## Required Prompts

The tests require these prompts in your PromptLayer workspace:

1. **multi-turn-assistant** - Basic conversation prompt
   - Placeholders: `{{chat_history}}`, `{{user_question}}`

2. **multi-turn-assistant-with-tools** - Tool-enabled prompt
   - Placeholders: `{{chat_history}}`, `{{user_question}}`, `{{ai_in_progress}}`
   - Tools: search_kb, create_ticket, escalate, end_conversation

See `TESTING_INSTRUCTIONS.md` in the parent directory for detailed setup.

## Adding New Tests

When adding tests:
1. Follow the existing naming convention: `test_[feature].py`
2. Include docstrings explaining what's being tested
3. Add the test to this README and TESTING_INSTRUCTIONS.md
4. Ensure tests can run independently