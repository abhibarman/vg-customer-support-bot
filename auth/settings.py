import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class OidcSettings:
    issuer: str
    client_id: str
    client_secret: str
    app_base_url: str
    session_secret: str
    scopes: str
    session_max_age: int

    @property
    def configured(self) -> bool:
        return bool(self.issuer and self.client_id and self.client_secret)

    @property
    def provider(self) -> str:
        host = self.issuer.lower()
        if "auth0.com" in host:
            return "auth0"
        if "okta.com" in host:
            return "okta"
        return "oidc"


def get_settings() -> OidcSettings:
    domain = os.environ.get("AUTH0_DOMAIN", "").strip().rstrip("/")
    issuer = os.environ.get("OIDC_ISSUER", "").strip().rstrip("/")
    if not issuer and domain:
        issuer = domain if domain.startswith("https://") else f"https://{domain}"
    return OidcSettings(
        issuer=issuer,
        client_id=os.environ.get("OIDC_CLIENT_ID", "").strip(),
        client_secret=os.environ.get("OIDC_CLIENT_SECRET", "").strip(),
        app_base_url=os.environ.get("APP_BASE_URL", "http://localhost:8000").rstrip("/"),
        session_secret=os.environ.get("SESSION_SECRET", "dev-only-change-me"),
        scopes=os.environ.get("OIDC_SCOPES", "openid profile email"),
        session_max_age=int(os.environ.get("OIDC_SESSION_MAX_AGE", str(60 * 60 * 8))),
    )


def is_configured() -> bool:
    return get_settings().configured
