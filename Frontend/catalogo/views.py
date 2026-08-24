import os
import requests
from django.shortcuts import render, redirect

API_URL_PRODUCTOS = os.getenv("API_URL_PRODUCTOS", "http://127.0.0.1:8000/productos")
API_URL_PEDIDOS = os.getenv("API_URL_PEDIDOS", "http://127.0.0.1:8000/pedidos")

# ==================== PRODUCTOS ====================

def listar_productos(request):
    productos = []
    try:
        response = requests.get(API_URL_PRODUCTOS)
        if response.status_code == 200:
            productos = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

    return render(request, 'catalogo/index.html', {'productos': productos})


def crear_producto(request):
    if request.method == 'POST':
        datos = {
            "nombre": request.POST.get('nombre'),
            "descripcion": request.POST.get('descripcion'),
            "precio": float(request.POST.get('precio')),
            "stock": int(request.POST.get('stock'))
        }
        try:
            requests.post(API_URL_PRODUCTOS, json=datos)
        except requests.exceptions.RequestException as e:
            print(f"Error al crear producto: {e}")
        return redirect('index')
    
    return render(request, 'catalogo/crear.html')


def editar_producto(request, producto_id):
    url_item = f"{API_URL_PRODUCTOS}/{producto_id}"
    
    if request.method == 'POST':
        datos = {
            "nombre": request.POST.get('nombre'),
            "descripcion": request.POST.get('descripcion'),
            "precio": float(request.POST.get('precio')),
            "stock": int(request.POST.get('stock'))
        }
        try:
            requests.put(url_item, json=datos)
        except requests.exceptions.RequestException as e:
            print(f"Error al editar producto: {e}")
        return redirect('index')

    producto = {}
    try:
        res = requests.get(url_item)
        if res.status_code == 200:
            producto = res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener producto: {e}")

    return render(request, 'catalogo/editar.html', {'producto': producto})


def eliminar_producto(request, producto_id):
    url_item = f"{API_URL_PRODUCTOS}/{producto_id}"
    try:
        requests.delete(url_item)
    except requests.exceptions.RequestException as e:
        print(f"Error al eliminar producto: {e}")
    return redirect('index')


# ==================== PEDIDOS ====================

def listar_pedidos(request):
    pedidos = []
    try:
        response = requests.get(API_URL_PEDIDOS)
        if response.status_code == 200:
            pedidos = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con pedidos: {e}")

    return render(request, 'catalogo/pedidos.html', {'pedidos': pedidos})


def crear_pedido(request):
    if request.method == 'POST':
        cliente_email = request.POST.get('cliente_email')
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad'))

        datos = {
            "cliente_email": cliente_email,
            "items": [
                {
                    "producto_id": producto_id,
                    "cantidad": cantidad
                }
            ]
        }
        try:
            requests.post(API_URL_PEDIDOS, json=datos)
        except requests.exceptions.RequestException as e:
            print(f"Error al crear pedido: {e}")
        return redirect('listar_pedidos')

    # Para seleccionar el producto en un desplegable
    productos = []
    try:
        res = requests.get(API_URL_PRODUCTOS)
        if res.status_code == 200:
            productos = res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos: {e}")

    return render(request, 'catalogo/crear_pedido.html', {'productos': productos})