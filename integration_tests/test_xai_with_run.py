from promptlayer import PromptLayer
from api_keys import API_KEYS

promptlayer = PromptLayer(api_key=API_KEYS["promptlayer"])

# Run a prompt template that uses your xAI custom provider
# (Your template should be configured to use a Grok model like grok-4-fast-reasoning)
response = promptlayer.run(
    prompt_name="grok-test",
    input_variables={"topic": "prompt engineering"}
)

# Access the response
print(response["raw_response"].choices[0].message.content)

# The request is automatically logged with request_id
print(f"\nRequest ID: {response['request_id']}")

