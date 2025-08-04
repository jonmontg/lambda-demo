from jinja2 import Environment, FileSystemLoader
import threading
import os
import json
from ..query_bedrock import query_model

def compound_method_worker(lock, bedrock, system_instructions, template, compound_method, prompt, updates, i):
  """
  Worker function to process a single compound method in parallel.

  This function is designed to run in a separate thread to process compound methods
  concurrently, improving performance when dealing with multiple compound methods.

  Args:
      lock (threading.Lock): Thread lock for safe access to shared updates dictionary
      bedrock: Bedrock client instance for AI model queries
      system_instructions (str): System instructions for the AI model
      template (jinja2.Template): Jinja2 template for rendering the prompt
      compound_method (dict): Individual compound method data to process
      prompt (str): User prompt describing the desired updates
      updates (dict): Shared dictionary to store results (thread-safe)
      i (int): Index of the compound method being processed

  Returns:
      None: Results are stored in the shared updates dictionary
  """
  # Query the AI model to get updates for this specific compound method
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
      updates["compound_methods"][str(i)] = compound_method_updates.get("updates", {})

def rule_context_update(s3, bedrock, assay_json, prompt, rule_name):
  """
  Main function to update assay context based on user prompt and rule definitions.

  This function orchestrates the entire process of updating assay data:
  1. Cleans and validates the user prompt using AI
  2. Retrieves rule definitions from S3
  3. Processes compound methods in parallel using worker threads
  4. Returns consolidated updates

  Args:
      s3: AWS S3 client for retrieving ruleset schema
      bedrock: Bedrock client for AI model interactions
      assay_json (dict): Complete assay data structure to be updated
      prompt (str): User prompt describing desired changes
      rule_name (str): Name of the rule to apply for context updates

  Returns:
      dict: Response with status code and body containing updates or error message
            - statusCode: 200 for success, 422 for validation errors
            - body: Dictionary of updates or error message
  """
  # Create thread lock for safe concurrent access to shared data
  lock = threading.Lock()

  # Initialize Jinja2 environment for template rendering
  # Templates are loaded from the templates directory relative to this file
  env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

  # Step 1: Clean the prompt using AI and rule definitions
  # Retrieve ruleset schema from S3 to understand rule structure and parameters
  ruleset_schema = s3.get_object(Bucket="assays-demo", Key="ruleset_schema.json")
  ruleset_schema = json.loads(ruleset_schema['Body'].read().decode('utf-8'))

  # Find the specific rule definition by name
  rule = next((rule for rule in ruleset_schema["ruleset_schema"]["rules"] if rule["name"] == rule_name), None)
  parameters = []
  if rule:
    # Extract rule parameters for prompt cleaning
    parameters = [param for param in rule["rule_parameters"]]

    # Create mapping between display names and internal names for AI processing
    word_map = {
      rule["display_name"]: rule["name"],
      **{param["display_name"]: param["name"] for param in parameters}
    }

    # Use AI to clean the prompt based on rule definitions
    clean_prompt_si = env.get_template("clean_prompt_si.j2").render(word_map = json.dumps(word_map))
    response = query_model(bedrock, clean_prompt_si, prompt)
    prompt = response["cleaned_prompt"]

  # Step 2: Validate the cleaned prompt
  validation_result = query_model(
    bedrock,
    env.get_template("validate_prompt_si.j2").render(
      rule_name = rule_name,
      rule_parameters = "\n".join([f"{param['name']}: {param['type']}" for param in parameters]) if any(parameters) else "none"
    ),
    prompt)

  # If validation fails, return error response
  if not validation_result.get("success", False):
    return {
      "statusCode": 422,
      "body": validation_result.get("response", "Internal error.")
    }

  # Step 3: Execute the validated prompt on the assay data
  # Prepare system instructions for AI processing
  system_instructions = env.get_template("update_assay_si.j2").render(
    rule_name=rule_name,
    rule_parameters="\n".join([f"{p['name']}: scope={p['scope']}, type={p['type']}" for p in parameters]) if any(parameters) else "none"
  )
  template = env.get_template("update_assay.j2")

  # Initialize results container and process compound methods in parallel
  updates = { "compound_methods": {} }
  threads = []

  # Create and start worker threads for each compound method
  for i in range(len(assay_json["compound_methods"])):
    t = threading.Thread(
      target=compound_method_worker,
      args=(lock, bedrock, system_instructions, template, assay_json["compound_methods"][i], prompt, updates, i)
    )
    t.start()
    threads.append(t)

  # Wait for all worker threads to complete
  for thread in threads:
    thread.join()

  # Return successful response with consolidated updates
  return {
    "statusCode": 200,
    "body": updates
  }