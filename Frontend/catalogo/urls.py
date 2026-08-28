from django.urls import path
from . import views

urlpatterns = [
    # Rutas de Productos
    path('', views.listar_productos, name='index'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<str:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<str:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # Upload de imagen
    path('api/upload-imagen/', views.subir_imagen, name='subir_imagen'),

    # Rutas de Pedidos
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/crear/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/eliminar/<str:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('pedidos/estado/<str:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
]
