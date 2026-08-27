from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# --- Modelos de Producto ---
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=120, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: float = Field(..., gt=0, description="El precio debe ser mayor a 0")
    stock: int = Field(..., ge=0, description="El stock no puede ser negativo")
    categoria: Optional[str] = Field(None, max_length=50)
    imagen_url: Optional[str] = Field(None, description="URL de imagen del producto")

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: str


# --- Modelos de Pedido ---
class ItemPedido(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a 0")

class ItemPedidoResponse(BaseModel):
    producto_id: str
    producto_nombre: Optional[str] = None
    cantidad: int
    precio_unitario: Optional[float] = None
    subtotal: Optional[float] = None

class PedidoCreate(BaseModel):
    cliente_nombre: Optional[str] = Field(None, max_length=120, description="Nombre del cliente")
    cliente_email: EmailStr
    cliente_telefono: Optional[str] = Field(None, max_length=20)
    notas: Optional[str] = Field(None, max_length=300, description="Notas adicionales del pedido")
    items: List[ItemPedido] = Field(..., min_length=1, description="Debe haber al menos un item")

class PedidoResponse(BaseModel):
    id: str
    cliente_nombre: Optional[str] = None
    cliente_email: EmailStr
    cliente_telefono: Optional[str] = None
    notas: Optional[str] = None
    items: List[ItemPedidoResponse]
    total: float
    estado: str = "pendiente"
    fecha_creacion: Optional[str] = None

class EstadoUpdate(BaseModel):
    estado: str
