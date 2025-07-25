import io, json, pytest, boto3
from botocore.response import StreamingBody
from botocore.stub import Stubber

@pytest.fixture
def bedrock_client():
    return boto3.client("bedrock-runtime", region_name="us-east-1")

def make_streaming_body(obj: dict) -> StreamingBody:
    data = json.dumps(obj).encode("utf-8")
    return StreamingBody(io.BytesIO(data), len(data))

@pytest.fixture
def stubbed_bedrock(bedrock_client):
    stubber = Stubber(bedrock_client)
    try:
        yield bedrock_client, stubber
    finally:
        stubber.deactivate()