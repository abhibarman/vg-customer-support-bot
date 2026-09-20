# Vanguard support chatbot

FastAPI app with a chat UI around the Amazon Bedrock Mantle-hosted MiniMax model,
scoped to Vanguard financial products and services.

**The API and the chat UI are the same process.** One `uvicorn` command starts both.

## Start (API + chat UI)

From this directory, after the one-time setup below:

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Leave that terminal running. Then in a browser open **http://localhost:8000** (not `127.0.0.1`).

| What | Where |
|---|---|
| Chat UI | [http://localhost:8000](http://localhost:8000) |
| Sign in | Button on that page (Auth0) |
| Health check | [http://localhost:8000/health](http://localhost:8000/health) |
| API docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Chat API | `POST http://localhost:8000/chat` (after sign-in) |

Stop the app with `Ctrl+C` in the terminal.

If port 8000 is already in use, either use that running server or stop it and start `uvicorn` again.

## First-time setup

### 1. Python env and dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

You also need:

- Python 3.12+ (3.14 works)
- AWS CLI profile `bedrock-role` (`aws configure list-profiles`)
- Network access to `https://bedrock-mantle.ap-south-1.api.aws`

### 2. Auth0 (required to use the chat)

1. Sign up at [https://auth0.com/signup](https://auth0.com/signup) (Gmail or org email is fine).
2. **Applications → Create Application** named `VG Support Chat`.
3. Type: **Regular Web Application**.
4. On **Settings**:
   - Allowed Callback URLs: `http://localhost:8000/auth/callback`
   - Allowed Logout URLs: `http://localhost:8000`
   - Allowed Web Origins: `http://localhost:8000`
5. Save, then copy **Domain**, **Client ID**, and **Client Secret** into `.env`:

```bash
APP_BASE_URL=http://localhost:8000
AUTH0_DOMAIN=your-tenant.us.auth0.com
OIDC_CLIENT_ID=...
OIDC_CLIENT_SECRET=...
SESSION_SECRET=any-long-random-string
```

Generate `SESSION_SECRET` with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start and use

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

1. Open [http://localhost:8000](http://localhost:8000).
2. Click **Sign in** and complete Auth0 login.
3. Use a suggested prompt or type in the box. Enter sends; Shift+Enter is a new line.
4. **New conversation** clears the thread. **Sign out** ends the Auth0 session.

Chat history lives in the browser only. Each turn posts prior messages to `POST /chat`.

## API after you are signed in

`POST /chat` needs the session cookie from the browser login. Easiest path is the UI. From curl, sign in via the UI first or you will get `401`.

```bash
curl http://localhost:8000/health
```

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

To continue a conversation, pass prior turns in `history`:

```json
{
  "message": "Which one is better for me?",
  "history": [
    { "role": "user", "content": "What is the difference between a Roth and Traditional 401k?" },
    { "role": "assistant", "content": "..." }
  ]
}
```

Optional Mantle smoke test (AWS only, no chat UI):

```bash
python bedrock-mantle.py
```

## Reuse the auth layer in another app

Auth is a generic OIDC package in `auth/`. Copy that folder (and optionally `static/auth-client.js`):

```python
from auth import mount_oidc, require_user

mount_oidc(app)

@app.get("/private")
def private(user: dict = Depends(require_user)):
    return user
```

See [`auth/README.md`](auth/README.md). To use Okta later, keep the same module and set `OIDC_ISSUER` instead of `AUTH0_DOMAIN`.

## Notes

- Default model: `minimax.minimax-m2.5` (`VG_BOT_MANTLE_MODEL` to override).
- Mantle uses short-lived IAM tokens from the `bedrock-role` AWS profile.
- CORS is wide open (`*`) — restrict `allow_origins` before deploying.
- Auth0's free plan is for development, not a production SLA.
- The system prompt is not licensed advice and cannot see account data.
