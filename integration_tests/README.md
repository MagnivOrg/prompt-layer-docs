# Integration Tests

**DO NOT COMMIT THIS FOLDER**

## Testing Philosophy

When testing custom provider integrations (Exa, xAI, etc.), **always use `promptlayer.run()`** with prompt templates from the PromptLayer dashboard.

### Why promptlayer.run()?

1. **Tests the full integration** - Dashboard → SDK → Provider
2. **Validates logging** - Ensures requests are properly tracked in PromptLayer
3. **Mirrors production usage** - This is how users will actually use the integrations
4. **Tests prompt templates** - Confirms custom providers work with the Prompt Registry

### Don't Use Direct SDK Calls

Avoid testing with direct LLM client calls that bypass PromptLayer. Instead, always use `promptlayer.run()` which tests the full integration flow through the prompt template system.

## Setup Requirements

Before running tests:
1. Set up the custom provider in PromptLayer dashboard (Settings → Custom Providers and Models)
2. Create a prompt template that uses the custom provider
3. Create `api_keys.py` in this folder with your API keys (see format below)

### API Keys Format

Create `integration_tests/api_keys.py`:
```python
API_KEYS = {
    "promptlayer": "pl_****",
    "exa": "****",
    "xai": "xai-****",
}
```

**Note:** `api_keys.py` is gitignored and should NOT be committed.

## Test Files

- `test_exa_with_run.py` - Tests Exa integration via promptlayer.run()
- `test_xai_with_run.py` - Tests xAI (Grok) integration via promptlayer.run()

## Running Tests

```bash
# From repo root
python integration_tests/test_exa_with_run.py
python integration_tests/test_xai_with_run.py
```

## Expected Output

Successful tests should:
- Print the AI response
- Return a `request_id` (confirms logging to PromptLayer)
- Include `prompt_blueprint` data showing the template used

