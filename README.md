# Tienda Online - Sistema Híbrido de Catálogo y Pedidos

Proyecto full stack para una Tienda Online, tienda especializada en hardware y accesorios tecnológicos. El sistema utiliza una arquitectura híbrida:

- **FastAPI** como microservicio de alto rendimiento para la gestión de productos y pedidos, conectado a **MongoDB Atlas**.
- **Django** como portal web cliente (patrón MVT), que consume la API mediante peticiones HTTP.

---

## 📁 Estructura del Proyecto

```text
mongo/
├── README.md
├── backend/    # API REST (FastAPI + MongoDB Atlas)
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env
│
└── frontend/   # Portal web (Django)
    ├── manage.py
    ├── Frontend/
    ├── catalogo/
    ├── requirements.txt
    └── .env
```

---

## 🚀 Backend (FastAPI)

### 1. Requisitos previos
- Python 3.10 o superior.
- Cuenta y clúster activo en MongoDB Atlas.

### 2. Instalación

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Variables de entorno

Crea un archivo `.env` dentro de `backend/` con:

```env
MONGO_URL=<tu_cadena_de_conexión_de_MongoDB_Atlas>
MONGO_DB_NAME=<nombre_de_tu_base_de_datos>
```

> ⚠️ No subas tu `.env` real al repositorio. Usa este ejemplo solo como referencia de las variables necesarias.

### 4. Ejecución

```bash
uvicorn main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`

---

## 🖥️ Frontend (Django)

### 1. Requisitos previos
- Python 3.10 o superior.
- Backend (FastAPI) corriendo y accesible.

### 2. Instalación

```bash
cd frontend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Variables de entorno

Crea un archivo `.env` dentro de `frontend/` con:

```env
API_URL_BASE=http://127.0.0.1:8000
DJANGO_SECRET_KEY=<tu_clave_secreta>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

### 4. Ejecución

```bash
python manage.py migrate
python manage.py runserver
```

El portal web quedará disponible en `http://127.0.0.1:8000` (si el backend usa otro puerto, ajusta `API_URL_BASE` en consecuencia, o corre el frontend en otro puerto con `runserver 8001`).

---

## 🔗 Endpoints principales de la API

| Método | Endpoint                          | Descripción                          |
|--------|------------------------------------|---------------------------------------|
| GET    | `/productos`                      | Lista productos (con filtros)         |
| POST   | `/productos`                      | Crea un producto                      |
| GET    | `/productos/{id}`                 | Obtiene un producto                   |
| PUT    | `/productos/{id}`                 | Actualiza un producto                 |
| PATCH  | `/productos/{id}`                 | Actualiza parcialmente un producto    |
| DELETE | `/productos/{id}`                 | Elimina un producto                   |
| POST   | `/pedidos`                        | Crea un pedido (valida stock)         |
| GET    | `/pedidos`                        | Lista pedidos (con filtros)           |
| GET    | `/pedidos/{id}`                   | Obtiene un pedido                     |
| PATCH  | `/pedidos/{id}/estado`            | Cambia el estado de un pedido         |
| DELETE | `/pedidos/{id}`                   | Elimina un pedido                     |
| GET    | `/stats`                          | Resumen general de la tienda          |

---

## ⚙️ Manejo de errores

- El frontend Django detecta si la API no responde (conexión caída o timeout) y muestra un aviso al usuario en vez de fallar silenciosamente.
- El backend valida `ObjectId`, existencia de recursos y stock disponible antes de procesar pedidos, devolviendo códigos HTTP apropiados (400, 404).

---
