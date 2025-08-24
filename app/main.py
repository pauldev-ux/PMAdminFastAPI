import os
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

# Fuerza qué .env cargar (simple y explícito)
env_file = os.getenv("APP_ENV_FILE", ".env.local")  # por defecto local
if os.path.exists(env_file):
    os.environ["PYDANTIC_ENV_FILE"] = env_file  # opcional: solo informativo


from app.core.config import settings
from app.core.cors import add_cors
from app.core.hosts import add_trusted_hosts

from app.api.deps import get_db
from app.db.session import Base, engine
from app.db import models
from app.core.static_files import add_static
from app.api.routes import brands, products, sales, auth

app = FastAPI(
    title="Perfumes Admin API",
    docs_url="/docs" if not settings.is_prod else None,
    redoc_url="/redoc" if not settings.is_prod else None,
    openapi_url="/openapi.json" if not settings.is_prod else None,
)

# Middlewares
add_trusted_hosts(app)
add_cors(app)
add_static(app)

# crea tablas al vuelo (luego pasamos a Alembic)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "name": "Perfumes Admin API",
        "env": settings.APP_ENV,
        "docs": "/docs" if not settings.is_prod else None,
        "health": "/health",
    }

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

# monta rutas
app.include_router(brands.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(auth.router)

