from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# --- USUARIOS ---
class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str = "cliente"

class UserResponse(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str

# --- PRODUCTOS ---
class ProductCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str

class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None

class ProductResponse(ProductCreate):
    id: str

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