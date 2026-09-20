from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from auth.client import get_oauth, logout_url
from auth.dependencies import get_session_user
from auth.settings import get_settings


def create_router(prefix: str = "/auth") -> APIRouter:
    router = APIRouter(prefix=prefix, tags=["auth"])

    @router.get("/me")
    def me(request: Request):
        settings = get_settings()
        user = get_session_user(request)
        if not user:
            return {
                "authenticated": False,
                "configured": settings.configured,
                "provider": settings.provider if settings.configured else None,
            }
        return {
            "authenticated": True,
            "configured": True,
            "provider": settings.provider,
            **user,
        }

    @router.get("/login")
    async def login(request: Request):
        settings = get_settings()
        if not settings.configured:
            raise HTTPException(
                status_code=503,
                detail="OIDC is not configured. Set OIDC_ISSUER (or AUTH0_DOMAIN), OIDC_CLIENT_ID, and OIDC_CLIENT_SECRET.",
            )
        redirect_uri = f"{settings.app_base_url}{prefix}/callback"
        return await get_oauth().oidc.authorize_redirect(request, redirect_uri)

    @router.get("/callback")
    async def callback(request: Request):
        settings = get_settings()
        if not settings.configured:
            raise HTTPException(status_code=503, detail="OIDC is not configured")
        try:
            token = await get_oauth().oidc.authorize_access_token(request)
        except Exception as exc:
            raise HTTPException(status_code=401, detail=f"Login failed: {exc}") from exc

        userinfo = token.get("userinfo") or {}
        request.session["user"] = {
            "sub": userinfo.get("sub"),
            "email": userinfo.get("email"),
            "name": userinfo.get("name")
            or userinfo.get("preferred_username")
            or userinfo.get("email"),
        }
        if token.get("id_token"):
            request.session["id_token"] = token["id_token"]
        return RedirectResponse(settings.app_base_url, status_code=302)

    @router.get("/logout")
    async def logout(request: Request):
        settings = get_settings()
        id_token = request.session.get("id_token")
        request.session.clear()
        destination = logout_url(settings, id_token) or settings.app_base_url
        return RedirectResponse(destination, status_code=302)

    return router
