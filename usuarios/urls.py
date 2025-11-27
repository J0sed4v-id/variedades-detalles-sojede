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
    path('reporte/pdf/', views.reporte_pdf, name='reporte_pdf'),

    # CRUD de productos
    path('productos/guardar/', views.agregar_producto, name='agregar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
 
    # Las APIs para la venta se mantienen igual
    path('api/buscar_producto/', views.buscar_producto_por_codigo, name='buscar_producto_codigo'),
    path('api/guardar_venta/', views.guardar_venta, name='guardar_venta'),
    path('api/listar_productos/', views.listar_todos_los_productos_api, name='listar_productos_api'),





    # Rutas para gestionar proveedores
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

path('facturas/', views.dashboard, name='facturas_placeholder'),
 path('factura/<int:venta_id>/pdf/', views.generar_factura_pdf, name='generar_factura_pdf'),
]
