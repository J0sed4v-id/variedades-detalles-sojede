from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Página principal
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar/', views.registrar, name='registrar'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'), 
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
    # Rutas adicionales para el dashboard
    path('buscar-habitaciones/', views.buscar_habitaciones, name='buscar_habitaciones'),
    path('habitaciones/', views.visualizar_habitaciones, name='visualizar_habitaciones'),  # Lista de habitaciones
    path('habitaciones/crear/', views.crear_habitacion, name='crear_habitacion'),  # Crear habitación
    path('habitaciones/<int:id>/editar/', views.actualizar_habitacion, name='actualizar_habitacion'),
    path('habitaciones/<int:id>/eliminar/', views.eliminar_habitacion, name='eliminar_habitacion'),
    path('visualizar-facturas/', views.visualizar_facturas, name='visualizar_facturas'),
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('generar-informe-ingresos/', views.generar_informe_ingresos, name='generar_informe_ingresos'),
    path('gestion_reservas/', views.gestionar_reservas, name='gestionar_reservas'),
    path('pagar-factura/<int:factura_id>/', views.pagar_factura, name='pagar_factura'),
]