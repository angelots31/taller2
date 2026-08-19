from fastapi import FastAPI, HTTPException, status
from bson import ObjectId
from database import productos_collection, pedidos_collection
from models import (
    ProductoCreate, 
    ProductoResponse, 
    PedidoCreate, 
    PedidoResponse
)

app = FastAPI(
    title="API REST - Tienda Online",
    description="Endpoints para gestión de Productos y Pedidos",
    version="1.0.0"
)

# Helper para convertir ObjectId a String
def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# --- RUTA INICIO ---

@app.get("/", tags=["Inicio"], summary="Mensaje de Bienvenida")
async def root():
    return {"mensaje": "¡Bienvenido a la API REST de TechGear!"}


# --- CRUD PRODUCTOS ---

@app.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"], summary="Crear Producto")
async def crear_producto(producto: ProductoCreate):
    nuevo = await productos_collection.insert_one(producto.model_dump())
    creado = await productos_collection.find_one({"_id": nuevo.inserted_id})
    return fix_id(creado)

@app.get("/productos", response_model=list[ProductoResponse], tags=["Productos"], summary="Listar Productos")
async def listar_productos():
    productos = []
    async for doc in productos_collection.find():
        productos.append(fix_id(doc))
    return productos

@app.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"], summary="Obtener Producto")
async def obtener_producto(producto_id: str):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    doc = await productos_collection.find_one({"_id": ObjectId(producto_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return fix_id(doc)

@app.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"], summary="Actualizar Producto")
async def actualizar_producto(producto_id: str, producto: ProductoCreate):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    resultado = await productos_collection.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": producto.model_dump()}
    )
    
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    doc = await productos_collection.find_one({"_id": ObjectId(producto_id)})
    return fix_id(doc)

@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"], summary="Eliminar Producto")
async def eliminar_producto(producto_id: str):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="ID inválido")
        
    resultado = await productos_collection.delete_one({"_id": ObjectId(producto_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None


# --- CRUD PEDIDOS ---

@app.post("/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED, tags=["Pedidos"], summary="Registrar Pedido")
async def crear_pedido(pedido: PedidoCreate):
    total = 0.0
    
    # Validar productos y calcular total
    for item in pedido.items:
        if not ObjectId.is_valid(item.producto_id):
            raise HTTPException(status_code=400, detail=f"ID inválido: {item.producto_id}")
        prod = await productos_collection.find_one({"_id": ObjectId(item.producto_id)})
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no existe")
        total += prod["precio"] * item.cantidad

    pedido_dict = pedido.model_dump()
    pedido_dict["total"] = total

    nuevo = await pedidos_collection.insert_one(pedido_dict)
    creado = await pedidos_collection.find_one({"_id": nuevo.inserted_id})
    return fix_id(creado)

@app.get("/pedidos", response_model=list[PedidoResponse], tags=["Pedidos"], summary="Listar Pedidos")
async def listar_pedidos():
    pedidos = []
    async for doc in pedidos_collection.find():
        pedidos.append(fix_id(doc))
    return pedidos

@app.get("/pedidos/{pedido_id}", response_model=PedidoResponse, tags=["Pedidos"], summary="Obtener Pedido")
async def obtener_pedido(pedido_id: str):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    doc = await pedidos_collection.find_one({"_id": ObjectId(pedido_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return fix_id(doc)

@app.delete("/pedidos/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Pedidos"], summary="Eliminar Pedido")
async def eliminar_pedido(pedido_id: str):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
    resultado = await pedidos_collection.delete_one({"_id": ObjectId(pedido_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return None