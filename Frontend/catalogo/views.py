import os
import uuid
import requests
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage

API_URL_BASE = os.getenv("API_URL_BASE", "https://taller2-4heu.onrender.com")
API_URL_PRODUCTOS = f"{API_URL_BASE}/productos"
API_URL_PEDIDOS = f"{API_URL_BASE}/pedidos"
API_TIMEOUT = 8

ESTADOS_PEDIDO = ["pendiente", "pagado", "enviado", "entregado", "cancelado"]


def api_call(method, url, **kwargs):
    """Ejecuta una petición a la API. Devuelve la respuesta o None si falla."""
    try:
        return requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        print(f"[API] Error de conexión: {url}")
        return None
    except requests.exceptions.Timeout:
        print(f"[API] Timeout: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[API] Error inesperado: {e}")
        return None


def aviso_error(request, accion="realizar la operación"):
    messages.error(request, f"No se pudo conectar al servidor. Verifica que la API esté corriendo antes de {accion}.")


def detalle_error(response, fallback):
    try:
        return response.json().get("detail", fallback)
    except (ValueError, AttributeError):
        return fallback


# ==================== PRODUCTOS ====================

def listar_productos(request):
    productos = []
    busqueda = request.GET.get("q", "")
    categoria = request.GET.get("categoria", "")

    params = {}
    if busqueda:
        params["q"] = busqueda
    if categoria:
        params["categoria"] = categoria

    response = api_call("GET", API_URL_PRODUCTOS, params=params)
    if response is None:
        aviso_error(request, "ver el catálogo")
    elif response.status_code == 200:
        productos = response.json()
    else:
        messages.error(request, "Error al obtener productos de la API.")

    # Obtener categorías únicas para el filtro
    categorias = sorted(set(p.get("categoria", "") for p in productos if p.get("categoria")))

    return render(request, 'catalogo/index.html', {
        'productos': productos,
        'busqueda': busqueda,
        'categoria_actual': categoria,
        'categorias': categorias,
    })


def crear_producto(request):
    if request.method == 'POST':
        datos = {
            "nombre": request.POST.get('nombre', '').strip(),
            "descripcion": request.POST.get('descripcion', '').strip(),
            "precio": float(request.POST.get('precio', 0)),
            "stock": int(request.POST.get('stock', 0)),
            "categoria": request.POST.get('categoria', '').strip() or None,
            "imagen_url": request.POST.get('imagen_url', '').strip() or None,
        }

        if not datos["nombre"]:
            messages.error(request, "El nombre es obligatorio.")
            return render(request, 'catalogo/crear.html', {'datos': datos})

        if datos["precio"] <= 0:
            messages.error(request, "El precio debe ser mayor a 0.")
            return render(request, 'catalogo/crear.html', {'datos': datos})

        if datos["stock"] < 0:
            messages.error(request, "El stock no puede ser negativo.")
            return render(request, 'catalogo/crear.html', {'datos': datos})

        response = api_call("POST", API_URL_PRODUCTOS, json=datos)
        if response is None:
            aviso_error(request, "crear el producto")
        elif response.status_code in (200, 201):
            messages.success(request, f"Producto '{datos['nombre']}' creado correctamente.")
            return redirect('index')
        else:
            messages.error(request, detalle_error(response, "No se pudo crear el producto."))

    return render(request, 'catalogo/crear.html')


def editar_producto(request, producto_id):
    url_item = f"{API_URL_PRODUCTOS}/{producto_id}"

    if request.method == 'POST':
        datos = {
            "nombre": request.POST.get('nombre', '').strip(),
            "descripcion": request.POST.get('descripcion', '').strip(),
            "precio": float(request.POST.get('precio', 0)),
            "stock": int(request.POST.get('stock', 0)),
            "categoria": request.POST.get('categoria', '').strip() or None,
            "imagen_url": request.POST.get('imagen_url', '').strip() or None,
        }

        if not datos["nombre"]:
            messages.error(request, "El nombre es obligatorio.")
        elif datos["precio"] <= 0:
            messages.error(request, "El precio debe ser mayor a 0.")
        elif datos["stock"] < 0:
            messages.error(request, "El stock no puede ser negativo.")
        else:
            response = api_call("PUT", url_item, json=datos)
            if response is None:
                aviso_error(request, "editar el producto")
            elif response.status_code == 200:
                messages.success(request, f"Producto '{datos['nombre']}' actualizado correctamente.")
                return redirect('index')
            else:
                messages.error(request, detalle_error(response, "No se pudo actualizar el producto."))

    producto = {}
    response = api_call("GET", url_item)
    if response is None:
        aviso_error(request, "cargar el producto")
    elif response.status_code == 200:
        producto = response.json()
    else:
        messages.error(request, "Producto no encontrado.")
        return redirect('index')

    return render(request, 'catalogo/editar.html', {'producto': producto})


def eliminar_producto(request, producto_id):
    response = api_call("DELETE", f"{API_URL_PRODUCTOS}/{producto_id}")
    if response is None:
        aviso_error(request, "eliminar el producto")
    elif response.status_code in (200, 204):
        messages.success(request, "Producto eliminado correctamente.")
    else:
        messages.error(request, detalle_error(response, "No se pudo eliminar el producto."))
    return redirect('index')


# ==================== PEDIDOS ====================

def listar_pedidos(request):
    pedidos = []
    filtro_estado = request.GET.get("estado", "")
    busqueda = request.GET.get("q", "")

    params = {}
    if filtro_estado:
        params["estado"] = filtro_estado
    if busqueda:
        params["cliente"] = busqueda

    response = api_call("GET", API_URL_PEDIDOS, params=params)
    if response is None:
        aviso_error(request, "ver los pedidos")
    elif response.status_code == 200:
        pedidos = response.json()
    else:
        messages.error(request, "Error al obtener pedidos de la API.")

    return render(request, 'catalogo/pedidos.html', {
        'pedidos': pedidos,
        'estados': ESTADOS_PEDIDO,
        'filtro_estado': filtro_estado,
        'busqueda': busqueda,
    })


def crear_pedido(request):
    if request.method == 'POST':
        cliente_nombre = request.POST.get('cliente_nombre', '').strip()
        cliente_email = request.POST.get('cliente_email', '').strip()
        cliente_telefono = request.POST.get('cliente_telefono', '').strip()
        notas = request.POST.get('notas', '').strip()
        producto_ids = request.POST.getlist('producto_ids')
        cantidades = request.POST.getlist('cantidades')

        # Validaciones del lado del servidor
        if not cliente_email:
            messages.error(request, "El correo del cliente es obligatorio.")
            return redirect('crear_pedido')

        items = []
        for pid, cant in zip(producto_ids, cantidades):
            pid = pid.strip()
            cant = cant.strip()
            if pid and cant:
                try:
                    cant_int = int(cant)
                    if cant_int > 0:
                        items.append({"producto_id": pid, "cantidad": cant_int})
                except ValueError:
                    pass

        if not items:
            messages.error(request, "Debes agregar al menos un producto al pedido.")
            return redirect('crear_pedido')

        datos = {
            "cliente_email": cliente_email,
            "items": items,
        }
        if cliente_nombre:
            datos["cliente_nombre"] = cliente_nombre
        if cliente_telefono:
            datos["cliente_telefono"] = cliente_telefono
        if notas:
            datos["notas"] = notas

        response = api_call("POST", API_URL_PEDIDOS, json=datos)
        if response is None:
            aviso_error(request, "crear el pedido")
        elif response.status_code in (200, 201):
            messages.success(request, "Pedido registrado correctamente.")
            return redirect('listar_pedidos')
        else:
            messages.error(request, detalle_error(response, "No se pudo registrar el pedido."))
        return redirect('crear_pedido')

    # Solo productos con stock disponible
    productos = []
    response = api_call("GET", API_URL_PRODUCTOS, params={"solo_con_stock": "true"})
    if response is None:
        aviso_error(request, "cargar los productos")
    elif response.status_code == 200:
        productos = response.json()

    return render(request, 'catalogo/crear_pedido.html', {'productos': productos})


def eliminar_pedido(request, pedido_id):
    response = api_call("DELETE", f"{API_URL_PEDIDOS}/{pedido_id}")
    if response is None:
        aviso_error(request, "eliminar el pedido")
    elif response.status_code in (200, 204):
        messages.success(request, "Pedido eliminado correctamente.")
    else:
        messages.error(request, detalle_error(response, "No se pudo eliminar el pedido."))
    return redirect('listar_pedidos')


def cambiar_estado_pedido(request, pedido_id):
    if request.method != 'POST':
        return redirect('listar_pedidos')

    estado = request.POST.get('estado')
    if estado not in ESTADOS_PEDIDO:
        messages.error(request, "Estado no valido.")
        return redirect('listar_pedidos')

    response = api_call("PATCH", f"{API_URL_PEDIDOS}/{pedido_id}/estado", json={"estado": estado})
    if response is None:
        aviso_error(request, "cambiar el estado del pedido")
    elif response.status_code == 200:
        messages.success(request, f"Estado del pedido actualizado a '{estado}'.")
    else:
        messages.error(request, "No se pudo actualizar el estado.")
    return redirect('listar_pedidos')


# ==================== UPLOAD DE IMAGEN ====================

def subir_imagen(request):
    """Recibe un archivo de imagen y lo guarda, devolviendo la URL."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    archivo = request.FILES.get('imagen')
    if not archivo:
        return JsonResponse({'error': 'No se envió ningún archivo'}, status=400)

    # Validar que sea imagen (acepta cualquier tipo de imagen)
    if not archivo.content_type or not archivo.content_type.startswith('image/'):
        return JsonResponse({'error': 'El archivo debe ser una imagen.'}, status=400)

    # Validar tamaño (max 50MB)
    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    if archivo.size > MAX_SIZE:
        return JsonResponse({'error': 'El archivo es demasiado grande (máximo 50MB).'}, status=400)

    # Guardar con nombre único
    ext = archivo.name.rsplit('.', 1)[-1].lower()
    nombre_unico = f"productos/{uuid.uuid4().hex}.{ext}"
    ruta_guardada = default_storage.save(nombre_unico, archivo)
    url_imagen = default_storage.url(ruta_guardada)

    return JsonResponse({'url': url_imagen})
