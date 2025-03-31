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
     path('reservar-habitacion/', views.reservar_habitacion, name='reservar_habitacion'),
    path('solicitar_servicio/', views.solicitar_servicio, name='solicitar_servicio'),
    path('visualizar-facturas/', views.visualizar_facturas, name='visualizar_facturas'),
    path('modificar-reserva/', views.modificar_reserva, name='modificar_reserva'),
    path('cancelar-reserva/', views.cancelar_reserva, name='cancelar_reserva'),
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('generar-pago/', views.generar_pago, name='generar_pago'),
    path('notificar-servicio/', views.notificar_servicio, name='notificar_servicio'),
    path('generar-informe-ingresos/', views.generar_informe_ingresos, name='generar_informe_ingresos'),
    path('solicitar-servicio/', views.solicitar_servicio, name='solicitar_servicio'),
]