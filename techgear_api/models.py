from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

# --- Modelos de Producto ---
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0, description="El precio debe ser mayor a 0")
    stock: int = Field(..., ge=0, description="El stock no puede ser negativo")

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: str

# --- Modelos de Pedido ---
class ItemPedido(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)

class PedidoCreate(BaseModel):
    cliente_email: EmailStr
    items: List[ItemPedido]

class PedidoResponse(BaseModel):
    id: str
    cliente_email: EmailStr
    items: List[ItemPedido]
    total: float