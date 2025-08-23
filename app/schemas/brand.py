from pydantic import BaseModel, ConfigDict

class BrandBase(BaseModel):
    nombre: str

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    nombre: str

class BrandOut(BrandBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
