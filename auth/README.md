# Reusable OIDC auth layer

Copy this `auth/` folder (and optionally `static/auth-client.js`) into another
FastAPI app. It talks **generic OIDC**, so Auth0, Okta, or another provider is
an environment-variable change.

## Install

```bash
pip install authlib httpx itsdangerous python-dotenv fastapi
```

## Wire it up

```python
from fastapi import Depends, FastAPI
from auth import mount_oidc, require_user, is_configured

app = FastAPI()
mount_oidc(app)  # adds /auth/login, /auth/callback, /auth/logout, /auth/me

@app.get("/private")
def private(user: dict = Depends(require_user)):
    return {"email": user.get("email")}
```

`require_user` returns `{sub, email, name}` from the session cookie.

## Environment

```bash
APP_BASE_URL=http://localhost:8000
SESSION_SECRET=long-random-string
OIDC_CLIENT_ID=...
OIDC_CLIENT_SECRET=...
```

Auth0 (either form):

```bash
AUTH0_DOMAIN=your-tenant.us.auth0.com
# or
OIDC_ISSUER=https://your-tenant.us.auth0.com
```

Okta Workforce:

```bash
OIDC_ISSUER=https://dev-xxxxx.okta.com/oauth2/default
```

Optional: `OIDC_SCOPES` (default `openid profile email`), `OIDC_SESSION_MAX_AGE` (seconds).

## Provider app settings

Register a **Regular Web Application** (confidential client) with:

- Callback: `{APP_BASE_URL}/auth/callback`
- Logout return: `{APP_BASE_URL}`
- Use `http://localhost:8000` consistently, not `127.0.0.1`

## Browser helper

`static/auth-client.js` exposes `OidcAuth.getSession()`. Copy it if the other
app has a web UI that should show a sign-in gate.
