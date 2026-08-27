from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from datetime import datetime, timezone
from database import productos_collection, pedidos_collection
from models import (
    ProductoCreate, 
    ProductoResponse, 
    PedidoCreate, 
    PedidoResponse,
    EstadoUpdate
)

ESTADOS_VALIDOS = {"pendiente", "pagado", "enviado", "entregado", "cancelado"}

app = FastAPI(
    title="API REST - Tienda Online",
    description="Endpoints para gestión de Productos y Pedidos",
    version="2.0.0"
)

# CORS para el frontend Django
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Helpers ----------

def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


async def enriquecer_pedido(doc):
    """Enriquece los items del pedido con nombre, precio unitario y subtotal."""
    cache = {}
    for item in doc.get("items", []):
        pid = str(item.get("producto_id"))
        if pid not in cache:
            prod = await productos_collection.find_one({"_id": ObjectId(pid)}) if ObjectId.is_valid(pid) else None
            cache[pid] = prod
        prod = cache[pid]
        if prod:
            item["producto_nombre"] = prod.get("nombre")
            item["precio_unitario"] = prod.get("precio", 0)
            item["subtotal"] = round(prod.get("precio", 0) * item.get("cantidad", 0), 2)
        else:
            item["producto_nombre"] = None
            item["precio_unitario"] = None
            item["subtotal"] = None
    return doc


def validate_object_id(oid: str, label: str = "ID"):
    if not ObjectId.is_valid(oid):
        raise HTTPException(status_code=400, detail=f"{label} inválido")
    return ObjectId(oid)


# ---------- Inicio ----------

@app.get("/", tags=["Inicio"], summary="Mensaje de Bienvenida")
async def root():
    return {"mensaje": "¡Bienvenido a la API REST de TechGear!", "version": "2.0"}


# ==================== CRUD PRODUCTOS ====================

@app.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"])
async def crear_producto(producto: ProductoCreate):
    nuevo = await productos_collection.insert_one(producto.model_dump())
    creado = await productos_collection.find_one({"_id": nuevo.inserted_id})
    return fix_id(creado)


@app.get("/productos", response_model=list[ProductoResponse], tags=["Productos"])
async def listar_productos(
    q: str = Query(None, description="Buscar por nombre o descripción"),
    categoria: str = Query(None, description="Filtrar por categoría"),
    min_precio: float = Query(None, ge=0, description="Precio mínimo"),
    max_precio: float = Query(None, ge=0, description="Precio máximo"),
    solo_con_stock: bool = Query(False, description="Solo productos con stock > 0"),
):
    filtro = {}
    if q:
        filtro["$or"] = [
            {"nombre": {"$regex": q, "$options": "i"}},
            {"descripcion": {"$regex": q, "$options": "i"}},
        ]
    if categoria:
        filtro["categoria"] = {"$regex": categoria, "$options": "i"}
    if min_precio is not None:
        filtro["precio"] = filtro.get("precio", {})
        filtro["precio"]["$gte"] = min_precio
    if max_precio is not None:
        filtro["precio"] = filtro.get("precio", {})
        filtro["precio"]["$lte"] = max_precio
    if solo_con_stock:
        filtro["stock"] = {"$gt": 0}

    productos = []
    async for doc in productos_collection.find(filtro).sort("nombre", 1):
        productos.append(fix_id(doc))
    return productos


@app.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
async def obtener_producto(producto_id: str):
    oid = validate_object_id(producto_id, "ID de producto")
    doc = await productos_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return fix_id(doc)


@app.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
async def actualizar_producto(producto_id: str, producto: ProductoCreate):
    oid = validate_object_id(producto_id, "ID de producto")
    resultado = await productos_collection.update_one(
        {"_id": oid}, {"$set": producto.model_dump(exclude_unset=True)}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    doc = await productos_collection.find_one({"_id": oid})
    return fix_id(doc)


@app.patch("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
async def actualizar_parcial_producto(producto_id: str, producto: ProductoCreate):
    """Actualización parcial — solo envía los campos que quieras cambiar."""
    oid = validate_object_id(producto_id, "ID de producto")
    data = {k: v for k, v in producto.model_dump(exclude_unset=True).items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    resultado = await productos_collection.update_one({"_id": oid}, {"$set": data})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    doc = await productos_collection.find_one({"_id": oid})
    return fix_id(doc)


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
async def eliminar_producto(producto_id: str):
    oid = validate_object_id(producto_id, "ID de producto")
    resultado = await productos_collection.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None


# ==================== CRUD PEDIDOS ====================

@app.post("/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
async def crear_pedido(pedido: PedidoCreate):
    total = 0.0
    productos_info = []

    # Validar productos, stock y calcular total
    for item in pedido.items:
        oid = validate_object_id(item.producto_id, "ID de producto")
        prod = await productos_collection.find_one({"_id": oid})
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto '{item.producto_id}' no existe")
        
        disponible = prod.get("stock", 0)
        if disponible < item.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente de '{prod['nombre']}' (disponible: {disponible}, solicitado: {item.cantidad})"
            )
        
        subtotal = prod["precio"] * item.cantidad
        total += subtotal
        productos_info.append({
            "producto_id": item.producto_id,
            "nombre": prod["nombre"],
            "precio": prod["precio"],
            "cantidad": item.cantidad,
            "subtotal": round(subtotal, 2),
        })

    # Descontar stock
    for item in pedido.items:
        await productos_collection.update_one(
            {"_id": ObjectId(item.producto_id)},
            {"$inc": {"stock": -item.cantidad}}
        )

    pedido_dict = pedido.model_dump()
    pedido_dict["total"] = round(total, 2)
    pedido_dict["estado"] = "pendiente"
    pedido_dict["fecha_creacion"] = datetime.now(timezone.utc).isoformat()

    nuevo = await pedidos_collection.insert_one(pedido_dict)
    creado = await pedidos_collection.find_one({"_id": nuevo.inserted_id})
    return await enriquecer_pedido(fix_id(creado))


@app.get("/pedidos", response_model=list[PedidoResponse], tags=["Pedidos"])
async def listar_pedidos(
    estado: str = Query(None, description="Filtrar por estado"),
    cliente: str = Query(None, description="Buscar por email o nombre del cliente"),
):
    filtro = {}
    if estado:
        if estado not in ESTADOS_VALIDOS:
            raise HTTPException(status_code=400, detail=f"Estado inválido. Valores: {sorted(ESTADOS_VALIDOS)}")
        filtro["estado"] = estado
    if cliente:
        filtro["$or"] = [
            {"cliente_email": {"$regex": cliente, "$options": "i"}},
            {"cliente_nombre": {"$regex": cliente, "$options": "i"}},
        ]

    pedidos = []
    async for doc in pedidos_collection.find(filtro).sort("fecha_creacion", -1):
        pedidos.append(await enriquecer_pedido(fix_id(doc)))
    return pedidos


@app.get("/pedidos/{pedido_id}", response_model=PedidoResponse, tags=["Pedidos"])
async def obtener_pedido(pedido_id: str):
    oid = validate_object_id(pedido_id, "ID de pedido")
    doc = await pedidos_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return await enriquecer_pedido(fix_id(doc))


@app.patch("/pedidos/{pedido_id}/estado", response_model=PedidoResponse, tags=["Pedidos"])
async def actualizar_estado_pedido(pedido_id: str, datos: EstadoUpdate):
    oid = validate_object_id(pedido_id, "ID de pedido")
    if datos.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Estado invalido. Valores permitidos: {sorted(ESTADOS_VALIDOS)}")

    resultado = await pedidos_collection.update_one(
        {"_id": oid}, {"$set": {"estado": datos.estado}}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    doc = await pedidos_collection.find_one({"_id": oid})
    return await enriquecer_pedido(fix_id(doc))


@app.delete("/pedidos/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Pedidos"])
async def eliminar_pedido(pedido_id: str):
    oid = validate_object_id(pedido_id, "ID de pedido")
    resultado = await pedidos_collection.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return None


# ==================== ESTADISTICAS ====================

@app.get("/stats", tags=["Estadisticas"], summary="Resumen general")
async def estadisticas():
    total_productos = await productos_collection.count_documents({})
    total_pedidos = await pedidos_collection.count_documents({})
    pedidos_pendientes = await pedidos_collection.count_documents({"estado": "pendiente"})
    
    ingresos = 0.0
    async for p in pedidos_collection.find({"estado": {"$in": ["pagado", "enviado", "entregado"]}}):
        ingresos += p.get("total", 0)
    
    return {
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "pedidos_pendientes": pedidos_pendientes,
        "ingresos_totales": round(ingresos, 2),
    }
