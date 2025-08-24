from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.core.config import settings

def add_static(app: FastAPI) -> None:
    base = Path(settings.STATIC_DIR)
    uploads = base / settings.UPLOADS_SUBDIR
    uploads.mkdir(parents=True, exist_ok=True)
    # Sirve todo el directorio /static
    app.mount("/static", StaticFiles(directory=str(base)), name="static")
