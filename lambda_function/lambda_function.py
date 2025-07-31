import json
import boto3
from src.rules.rule_context_update import rule_context_update

def lambda_handler(event, _):
  bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
  s3 = boto3.client("s3", region_name="us-east-1")
  prompt = event.get("user_prompt")
  assay_name = event.get("assay_name")
  prompt_context = event.get("prompt_context")

  assay_file = s3.get_object(
    Bucket="assays-demo",
    Key=assay_name
  )
  assay_json = json.loads(assay_file['Body'].read().decode('utf-8'))

  # Select the action by prompt context
  if prompt_context and prompt_context.startswith("rules:"):
    return rule_context_update(s3, bedrock, assay_json, prompt, prompt_context.split(":")[1])
  else:
    return {
      "statusCode": 422,
      "body": "Updates on this page are unsupported at this time. Coming soon..."
    }
