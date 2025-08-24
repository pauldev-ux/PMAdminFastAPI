from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings

def add_trusted_hosts(app: FastAPI) -> None:
    hosts = [h.strip() for h in settings.TRUSTED_HOSTS.split(",") if h.strip()]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts or ["*"])
