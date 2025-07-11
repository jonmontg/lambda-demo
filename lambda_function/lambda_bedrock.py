import logging
import json
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def query_model(bedrock, system, message):
  response = bedrock.invoke_model(
    modelId="amazon.nova-micro-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
      "schemaVersion": "messages-v1",
      "system": [{"text": system}],
      "messages": [{"role": "user", "content": [{"text": message}]}],
      "inferenceConfig": {
        "maxTokens": 10000
      }
    })
  )
  response = json.loads(response["body"].read())
  logger.info(f"Prompt: {message}")
  logger.info(f"Model response text: {str(response)}")
  parsed_response = re.sub(r"^```json|```$", "", response["output"]["message"]["content"][0]["text"].strip())
  parsed_response = parsed_response.encode().decode("unicode_escape")
  return json.loads(parsed_response)