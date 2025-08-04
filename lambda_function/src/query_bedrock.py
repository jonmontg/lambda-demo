import logging
import json
import re
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def query_model(bedrock, system, message, max_attempts=7, base_delay=0.5, backoff_factor=2):
  payload = {
    "schemaVersion": "messages-v1",
    "system": [{"text": system}],
    "messages": [{"role": "user", "content": [{"text": message}]}],
    "inferenceConfig": {
      "temperature": 0.7,
      "maxTokens": 10000
    }
  }

  attempt = 0
  while True:
    try:
      response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
          "schemaVersion": "messages-v1",
          "system": [{"text": system}],
          "messages": [{"role": "user", "content": [{"text": message}]}],
          "inferenceConfig": {
            "temperature": 0.7,
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
    except bedrock.exceptions.ThrottlingException:
      pass

    attempt += 1
    if attempt >= max_attempts:
      logger.error("Giving up after %d throttling retries", attempt)
      raise
    delay = base_delay * (backoff_factor ** (attempt - 1))
    logger.warning("Bedrock throttled (attempt %d/%d); sleeping %.2fs",
                    attempt, max_attempts, delay)
    time.sleep(delay)