from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# --- USUARIOS ---
class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str = "cliente"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str

# --- PRODUCTOS ---
class ProductCreate(BaseModel):
    nombre: str = Field(min_length=1)
    descripcion: str
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    categoria: str

class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    categoria: Optional[str] = None

class ProductResponse(BaseModel):
    # Modelo propio: no hereda las validaciones de ProductCreate,
    # asi los productos antiguos (precio 0, stock 0) siguen listandose.
    id: str
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str

# --- PEDIDOS ---
class OrderItem(BaseModel):
    product_id: str
    cantidad: int
    precio_unitario: float

class OrderCreate(BaseModel):
    usuario_id: str
    items: List[OrderItem]

class OrderResponse(BaseModel):
    id: str
    usuario_id: str
    items: List[OrderItem]
    total: float
    fecha: datetime