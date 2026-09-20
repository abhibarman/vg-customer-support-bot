import os
from typing import Literal

from aws_bedrock_token_generator import provide_token
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

# --- Config ---------------------------------------------------------------

MANTLE_BASE_URL = os.environ.get("VG_BOT_MANTLE_BASE_URL", "https://bedrock-mantle.ap-south-1.api.aws/v1")
MANTLE_PROJECT = os.environ.get("VG_BOT_MANTLE_PROJECT", "default")
MANTLE_REGION = os.environ.get("VG_BOT_MANTLE_REGION", "ap-south-1")
MODEL_NAME = os.environ.get("VG_BOT_MANTLE_MODEL", "minimax.minimax-m2.5")


def get_mantle_client() -> OpenAI:
    """Return a Mantle client authenticated by a short-lived IAM token.

    Mantle scopes tokens to the endpoint region.  It uses the named profile
    configured for REDVERSE (``bedrock-role`` by default), never an API key.
    A new client/token is created per request so long-running demos do not
    reuse an expired credential.
    """
    os.environ.setdefault("AWS_PROFILE", os.environ.get("REDVERSE_AWS_PROFILE", "bedrock-role"))
    os.environ["AWS_REGION"] = MANTLE_REGION
    os.environ["AWS_DEFAULT_REGION"] = MANTLE_REGION
    return OpenAI(
        api_key=provide_token(),
        base_url=MANTLE_BASE_URL.rstrip("/"),
        project=MANTLE_PROJECT,
        timeout=float(os.environ.get("VG_BOT_MANTLE_TIMEOUT", "120")),
    )

SYSTEM_PROMPT = """You are Vanguard's customer support assistant. You help customers with \
questions about Vanguard financial products and services, including 401(k) plans, IRAs, \
brokerage accounts, mutual funds, ETFs, fees, account management, and general investing \
concepts as they relate to Vanguard offerings.

Rules:
- Only answer questions about Vanguard products, services, and general account/investing \
mechanics. If asked something unrelated, politely redirect to Vanguard-related topics.
- You are not a licensed financial advisor. For personalized investment advice (what to buy, \
how to allocate, tax strategy specific to the user's situation), tell the user you can explain \
the options and mechanics, but recommend they speak with a Vanguard advisor for personalized \
recommendations.
- Be clear, concise, and avoid jargon unless the user demonstrates familiarity with it.
- Never fabricate specific account details, balances, or transaction data \u2014 you do not have \
access to any individual's account. If asked about "my balance" or similar, explain that you \
can't access account-specific data and point them to logging into their account or contacting \
support directly.
"""

# --- App --------------------------------------------------------------------

app = FastAPI(title="Vanguard Support Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before anything beyond local dev
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's latest message")
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior turns in the conversation, oldest first (excluding system prompt)",
    )


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    try:
        completion = get_mantle_client().chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            top_p=0.95,
            max_tokens=2048,
            stream=False,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream model error: {e}")

    reply = completion.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="Empty response from model")

    return ChatResponse(reply=reply)
