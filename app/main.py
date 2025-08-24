from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
# 👇 importa Base/engine y registra modelos
from app.db.session import Base, engine
from app.db import models

from app.api.routes import brands
from app.api.routes import products
from app.api.routes import sales

app = FastAPI(title="Perfumes Admin API")

# crea tablas al vuelo (luego pasamos a Alembic)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"name": "Perfumes Admin API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

# monta rutas
app.include_router(brands.router)
app.include_router(products.router)
app.include_router(sales.router)
