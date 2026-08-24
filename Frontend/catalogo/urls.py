from django.urls import path
from . import views

urlpatterns = [
    # Rutas de Productos
    path('', views.listar_productos, name='index'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<str:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<str:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # Rutas de Pedidos
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/crear/', views.crear_pedido, name='crear_pedido'),
]