from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from auth.router import create_router
from auth.settings import get_settings


def mount_oidc(app: FastAPI, *, prefix: str = "/auth") -> None:
    """Attach session cookies and OIDC routes to any FastAPI app."""
    settings = get_settings()
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        same_site="lax",
        https_only=settings.app_base_url.startswith("https://"),
        max_age=settings.session_max_age,
    )
    app.include_router(create_router(prefix))
