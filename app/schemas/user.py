from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str | None
    email: str | None
    is_active: bool
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
