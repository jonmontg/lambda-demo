from lambda_function import lambda_handler
import yaml, json, pathlib
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_golden_cases():
  base = pathlib.Path(__file__).parent.parent / "golden"
  cfg = yaml.safe_load((base / "cases.yml").read_text())

  for case in cfg["cases"]:
    logger.info(f"Test: {case['id']}")
    response = lambda_handler(case.get("event"), None)
    response["body"] = response["body"]

    if case["expect"]["mode"] == "exact":
      with open(case["expect"]["file"]) as f:
        exp = json.load(f)
      assert exp == response
    elif case["expect"]["mode"] == "status":
      with open(case["expect"]["file"]) as f:
        exp = json.load(f)
      assert exp["statusCode"] == response.get("statusCode")
    else:
       assert False