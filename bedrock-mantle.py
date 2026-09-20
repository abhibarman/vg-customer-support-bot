import os

from openai import OpenAI
from aws_bedrock_token_generator import provide_token

# A small standalone Mantle smoke test. The FastAPI app uses the same settings.
os.environ.setdefault("AWS_PROFILE", os.environ.get("REDVERSE_AWS_PROFILE", "bedrock-role"))
os.environ["AWS_REGION"] = os.environ.get("VG_BOT_MANTLE_REGION", "ap-south-1")
os.environ["AWS_DEFAULT_REGION"] = os.environ["AWS_REGION"]

client = OpenAI(
    api_key=provide_token(),
    base_url=os.environ.get("VG_BOT_MANTLE_BASE_URL", "https://bedrock-mantle.ap-south-1.api.aws/v1"),
    project=os.environ.get("VG_BOT_MANTLE_PROJECT", "default"),
)

response = client.chat.completions.create(
    model=os.environ.get("VG_BOT_MANTLE_MODEL", "minimax.minimax-m2.5"),
    messages=[{"role": "user", "content": "Summarize this document..."}],
    stream=False,
)

print(response.choices[0].message.content or "")
