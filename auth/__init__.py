"""Reusable OIDC auth layer for FastAPI apps.

Copy this `auth` package into another project, install
`authlib`, `httpx`, and `itsdangerous`, then:

    from auth import mount_oidc, require_user

    mount_oidc(app)

    @app.get("/private")
    def private(user: dict = Depends(require_user)):
        return user

Configure with OIDC_* environment variables. Auth0, Okta, and other
OIDC providers work by changing the issuer URL.
"""

from auth.dependencies import get_session_user, require_user
from auth.mount import mount_oidc
from auth.settings import get_settings, is_configured

__all__ = [
    "get_session_user",
    "get_settings",
    "is_configured",
    "mount_oidc",
    "require_user",
]
