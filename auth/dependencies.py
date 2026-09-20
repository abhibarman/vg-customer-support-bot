from typing import Optional

from fastapi import HTTPException, Request


def get_session_user(request: Request) -> Optional[dict]:
    return request.session.get("user")


def require_user(request: Request) -> dict:
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Sign in required")
    return user
