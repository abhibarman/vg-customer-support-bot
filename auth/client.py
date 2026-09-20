from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuth

from auth.settings import OidcSettings, get_settings

_oauth = OAuth()
_registered = False


def get_oauth() -> OAuth:
    global _registered
    settings = get_settings()
    if settings.configured and not _registered:
        _oauth.register(
            name="oidc",
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            server_metadata_url=f"{settings.issuer}/.well-known/openid-configuration",
            client_kwargs={"scope": settings.scopes},
        )
        _registered = True
    return _oauth


def logout_url(settings: OidcSettings, id_token: str | None) -> str | None:
    """Build a provider logout URL. Auth0 uses /v2/logout; others use OIDC RP logout."""
    if not settings.configured:
        return None
    if settings.provider == "auth0":
        return (
            f"{settings.issuer}/v2/logout?"
            f"{urlencode({'client_id': settings.client_id, 'returnTo': settings.app_base_url})}"
        )
    if id_token:
        return (
            f"{settings.issuer}/v1/logout?"
            f"{urlencode({'id_token_hint': id_token, 'post_logout_redirect_uri': settings.app_base_url})}"
        )
    return None
