from app.db.session import SessionLocal

# Dependencia de DB para inyectar en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
