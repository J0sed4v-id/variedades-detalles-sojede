from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar/', views.registrar, name='registrar'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),

    # Acceso desde dashboard
    path('productos/', views.listar_productos, name='productos'),
    path('inventario/', views.gestionar_inventario, name='inventario'),
    path('compras/', views.registrar_venta, name='compras'),
    path('reportes/', views.reportes, name='reportes'),  # Ruta para reportes

    # CRUD de productos
    path('productos/guardar/', views.agregar_producto, name='agregar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # Rutas para gestionar proveedores
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
]
