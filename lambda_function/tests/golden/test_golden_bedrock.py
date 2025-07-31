from lambda_function import lambda_handler
import yaml, json, pathlib
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run_test(tid, expected, actual):
  logger.info(f"""
Test: {tid}.
==========
Expected={expected}
Actual={actual}
  """)
  assert expected == actual


def test_golden_cases():
  base = pathlib.Path(__file__).parent.parent / "golden"
  cfg = yaml.safe_load((base / "cases.yml").read_text())

  for case in cfg["cases"]:
    response = lambda_handler(case.get("event"), None)
    response["body"] = json.loads(response["body"])

    if case["expect"]["mode"] == "exact":
      with open(case["expect"]["file"]) as f:
        exp = json.load(f)
      run_test(case["id"], exp, response)
    elif case["expect"]["mode"] == "status":
      with open(case["expect"]["file"]) as f:
        exp = json.load(f)
      run_test(case["id"],  exp["statusCode"], response.get("statusCode"))
    else:
       assert False