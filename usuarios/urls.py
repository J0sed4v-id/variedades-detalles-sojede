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
    
    # La URL 'compras' ahora apunta a la vista de registrar venta (TPV)
    path('compras/', views.registrar_venta, name='compras'),
    
    # Dejamos 'facturas' como un placeholder para el futuro
    path('facturas/', views.dashboard, name='facturas_placeholder'),

    # La vieja funcionalidad de compras ya no se usa en la URL principal
    path('comprar_producto/<int:producto_id>/', views.comprar_producto, name='comprar_producto'),
    path('compras/pagar/<int:compra_id>/', views.pagar_compra, name='pagar_compra'),

    # CRUD de productos
    path('productos/guardar/', views.agregar_producto, name='agregar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # Nueva ruta para autocompletado
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    path('productos/buscar/', views.buscar_productos, name='buscar_productos'),

    # Las APIs para la venta se mantienen igual
    path('api/buscar_producto/', views.buscar_producto_por_codigo, name='buscar_producto_codigo'),
    path('api/guardar_venta/', views.guardar_venta, name='guardar_venta'),
    path('api/listar_productos/', views.listar_todos_los_productos_api, name='listar_productos_api'),

    # ✅ Nueva ruta para generar la factura PDF térmica
    path('factura/<int:venta_id>/pdf/', views.generar_factura_pdf, name='generar_factura_pdf'),

# ✅ Nuevas rutas para generar reportes en diferentes formatos
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('reportes/excel/', views.reporte_excel, name='reporte_excel'),


]
