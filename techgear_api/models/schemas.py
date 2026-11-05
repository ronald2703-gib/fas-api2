from pydantic import BaseModel, Field, EmailStr, AfterValidator
from typing import Annotated, List, Optional, Literal
from datetime import datetime

# Imagen: URL http(s) o data-URI (la web la reduce a ~640px antes de enviarla)
MAX_IMAGE_CHARS = 350_000
_IMAGE_PREFIXES = ("http://", "https://", "data:image/png;base64,", "data:image/jpeg;base64,",
                   "data:image/webp;base64,", "data:image/gif;base64,")

def _check_image(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip()
    if v == "":
        return ""
    if len(v) > MAX_IMAGE_CHARS:
        raise ValueError("La imagen es demasiado grande")
    if not v.lower().startswith(_IMAGE_PREFIXES):
        raise ValueError("La imagen debe ser una URL http(s) o una imagen png/jpeg/webp/gif")
    return v

ImageStr = Annotated[Optional[str], AfterValidator(_check_image)]

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
    imagen: ImageStr = None

class ProductUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    categoria: Optional[str] = None
    imagen: ImageStr = None  # "" = quitar imagen

class ProductResponse(BaseModel):
    # Modelo propio: no hereda las validaciones de ProductCreate,
    # asi los productos antiguos (precio 0, stock 0) siguen listandose.
    id: str
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str
    imagen: Optional[str] = None

# --- PEDIDOS ---
class OrderItemCreate(BaseModel):
    # El precio NO se recibe: el servidor lo toma del producto
    product_id: str
    cantidad: int = Field(ge=1, le=100)

class OrderItem(BaseModel):
    product_id: str
    nombre: Optional[str] = None
    cantidad: int
    precio_unitario: float

class OrderCreate(BaseModel):
    # El usuario sale del token JWT, no del body
    items: List[OrderItemCreate] = Field(min_length=1)
    # Imagen del pedido (opcional). Si no se envia, se usa la del primer producto.
    imagen: ImageStr = None

class OrderStatusUpdate(BaseModel):
    estado: Literal["comprado", "cancelado"]

class OrderResponse(BaseModel):
    id: str
    usuario_id: str
    items: List[OrderItem]
    total: float
    fecha: datetime
    estado: str = "pendiente"  # pendiente | comprado | cancelado
    imagen: Optional[str] = None
