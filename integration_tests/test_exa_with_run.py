from promptlayer import PromptLayer
from api_keys import API_KEYS

promptlayer = PromptLayer(api_key=API_KEYS["promptlayer"])

# Run a prompt template that uses your Exa custom provider
response = promptlayer.run(
    prompt_name="exa-test",
    input_variables={"name": "Jared Zoneraich"}
)

# Access the response
print(response["raw_response"].choices[0].message.content)

# The request is automatically logged with request_id
print(f"\nRequest ID: {response['request_id']}")

