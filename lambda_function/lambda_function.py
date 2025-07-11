import json
import boto3
import os
from jinja2 import Environment, FileSystemLoader
import threading
from lambda_actions import validate_prompt, modify_assay

lock = threading.Lock()

def lambda_handler(event, context):
  bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
  s3 = boto3.client("s3", region_name="us-east-1")
  prompt = event.get("user_prompt")
  env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
  assay_name = event.get("assay_name")
  assay_file = s3.get_object(
    Bucket="assays-demo",
    Key=assay_name
  )
  assay_json = json.loads(assay_file['Body'].read().decode('utf-8'))

  # Validate the prompt
  validation_result = validate_prompt(bedrock, env, prompt)
  if not validation_result.get("success", False):
    return {
      "statusCode": 400,
      "body": validation_result.get("response")
    }

  # Execute the prompt on the chunked assay
  updates = modify_assay(lock, bedrock, env, prompt, assay_json)

  return {
    "statusCode": 200,
    "body": json.dumps(updates)
  }
