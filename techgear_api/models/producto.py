from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field, HttpUrl

PyObjectId = Annotated[str, BeforeValidator(str)]

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    categoria: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    imagen_url: Optional[HttpUrl] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
