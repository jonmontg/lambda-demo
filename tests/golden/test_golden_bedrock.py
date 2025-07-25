from lambda_function.lambda_function import lambda_handler
import yaml, json, pathlib


def test_golden_cases():
  base = pathlib.Path(__file__).parent.parent / "golden"
  cfg = yaml.safe_load((base / "cases.yml").read_text())

  for case in cfg["cases"]:
    response = lambda_handler(case.get("event"), None)

    if case["expect"] == "exact":
      with open(case["expect"]["file"]) as f:
          exp = json.load(f)
      assert response == exp