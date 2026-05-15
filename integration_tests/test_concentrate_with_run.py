from promptlayer import PromptLayer
from api_keys import API_KEYS

promptlayer = PromptLayer(api_key=API_KEYS["promptlayer"])

# Run a prompt template that uses your Concentrate custom provider
# (Your template should be configured to use a Concentrate model like
# claude-opus-4-7, gpt-5.5, or anthropic/claude-opus-4-7)
response = promptlayer.run(
    prompt_name="concentrate-test",
    input_variables={"topic": "prompt engineering"}
)

# Access the response (template is configured for the Responses API)
print(response["raw_response"].output_text)

# The request is automatically logged with request_id
print(f"\nRequest ID: {response['request_id']}")
