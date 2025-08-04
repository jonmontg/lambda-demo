import logging
import json
import re
import time

# Configure logging for the module
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def query_model(bedrock, system, message, max_attempts=7, base_delay=0.5, backoff_factor=2):
  """
  Query Amazon Bedrock's Nova Pro model with retry logic and error handling.

  Args:
      bedrock: Bedrock client instance for making API calls
      system (str): System prompt/context to provide to the model
      message (str): User message/query to send to the model
      max_attempts (int): Maximum number of retry attempts for throttling (default: 7)
      base_delay (float): Base delay in seconds for exponential backoff (default: 0.5)
      backoff_factor (float): Multiplier for exponential backoff (default: 2)

  Returns:
      dict: Parsed JSON response from the model

  Raises:
      Exception: If max retry attempts are exceeded or other errors occur
  """

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