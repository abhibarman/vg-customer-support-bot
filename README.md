# Vanguard support chatbot API

Minimal FastAPI wrapper around the Amazon Bedrock Mantle-hosted MiniMax model, scoped to answer questions
about Vanguard financial products and services.

## Prerequisites

- Python 3.12+ (3.14 works)
- AWS CLI with a `bedrock-role` profile that can assume the Mantle/Bedrock IAM role
- Network access to `https://bedrock-mantle.ap-south-1.api.aws`

Confirm the profile exists:

```bash
aws configure list-profiles
```

## Setup

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` is optional if `AWS_PROFILE=bedrock-role` is already in your environment. The
defaults in `.env.example` match the Mantle endpoint used by this app.

With [uv](https://docs.astral.sh/uv/) instead of pip:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

The API is at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

Health check:

```bash
curl http://localhost:8000/health
```

Optional Mantle smoke test (same credentials as the API):

```bash
python bedrock-mantle.py
```

## Usage

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the difference between a Roth and Traditional 401k?",
    "history": []
  }'
```

Response:

```json
{ "reply": "..." }
```

To continue a conversation, pass prior turns back in `history`:

```json
{
  "message": "Which one is better for me?",
  "history": [
    { "role": "user", "content": "What is the difference between a Roth and Traditional 401k?" },
    { "role": "assistant", "content": "..." }
  ]
}
```

## Notes / next steps

- The default model is `minimax.minimax-m2.5`. Override it with
  `VG_BOT_MANTLE_MODEL` only when a different model is available in Mantle.
- Mantle uses short-lived IAM tokens from the `bedrock-role` AWS profile; no
  model API key is stored in the demo app.
- CORS is wide open (`*`) — restrict `allow_origins` before deploying anywhere real.
- No conversation persistence, rate limiting, or auth yet — fine for a same-day demo,
  not for anything customer-facing.
- The system prompt scopes answers to Vanguard topics and explicitly avoids acting as
  a licensed advisor or fabricating account-specific data. Worth a compliance review
  before this touches real users.
