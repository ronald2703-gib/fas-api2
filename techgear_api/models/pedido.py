from typing import List, Optional
from pydantic import BaseModel, Field

class ItemPedido(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)

class PedidoCreate(BaseModel):
    cliente_nombre: str = Field(..., min_length=2)
    cliente_correo: str
    items: List[ItemPedido]
    total: float = Field(..., gt=0)

class PedidoResponse(PedidoCreate):
    id: str = Field(alias="_id")
    estado: str = "pendiente"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
