from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import settings

def add_cors(app: FastAPI) -> None:
    origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
