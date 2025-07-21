from jinja2 import Environment, FileSystemLoader
import threading
import os
import json
from lambda_bedrock import query_model

def compound_method_worker(lock, bedrock, system_instructions, template, compound_method, prompt, updates, i):
  compound_method_updates = query_model(
    bedrock,
    system_instructions,
    template.render(
      assay_json=compound_method,
      user_prompt=prompt,
      description="compound method and associated chromatogram methods"
    )
  )
  if compound_method_updates.get("should_update", False):
    with lock:
      updates["compound_methods"]["i"] = compound_method_updates.get("updates", {})

def rule_context_update(s3, bedrock, assay_json, prompt, rule_name):
  lock = threading.Lock()
  env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates", "rule_setting_update")))

  # Validate the prompt
  validation_result = query_model(bedrock, env.get_template("validate_prompt_si.j2").render(), prompt)
  if not validation_result.get("success", False):
    return {
      "statusCode": 400,
      "body": validation_result.get("response")
    }

  # Clean the prompt
  ruleset_schema = s3.get_object(Bucket="assays-demo", Key="ruleset_schema")
  ruleset_schema = json.loads(ruleset_schema['Body'].read().decode('utf-8'))
  rule = next((rule for rule in ruleset_schema["ruleset_schema"]["rules"] if rule["name"] == rule_name), None)
  if rule:
    word_map = {
      rule["display_name"]: rule["name"],
      **{param["display_name"]: param["name"] for param in rule["rule_parameters"]}
    }
    clean_prompt_si = env.get_template("clean_prompt_si.j2").render(word_map = json.dumps(word_map))
    response = query_model(bedrock, clean_prompt_si, prompt)
    prompt = response["cleaned_prompt"]

  # Execute the prompt on the chunked assay
  system_instructions = env.get_template("update_assay_si.j2").render()
  template = env.get_template("update_assay.j2")

  updates = { "compound_methods": {} }
  threads = []
  for i in range(len(assay_json["compound_methods"])):
    t = threading.Thread(
      target=compound_method_worker,
      args=(lock, bedrock, system_instructions, template, assay_json["compound_methods"][i], prompt, updates, i)
    )
    t.start()
    threads.append(t)
  for thread in threads:
    thread.join()

  return {
    "statusCode": 200,
    "body": json.dumps(updates)
  }