import threading
from lambda_bedrock import query_model

def validate_prompt(bedrock, env, prompt):
  system_instructions = env.get_template("validate_prompt_si.j2").render()
  validation_result = query_model(bedrock, system_instructions, prompt)
  return validation_result

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
      updates["compound_methods"][i] = compound_method_updates.get("updates", {})

def modify_assay(lock, bedrock, env, prompt, assay_json):
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

  return updates