from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Página principal
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar/', views.registrar, name='registrar'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'), 
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
    # Acceso desde dashboard
    path('productos/', views.gestionar_productos, name='productos'),
    path('inventario/', views.gestionar_reservas, name='inventario'),   # ajustar si necesitas otra vista
    path('compras/', views.visualizar_facturas, name='compras'),       # ajustar si necesitas otra vista

    # CRUD de habitaciones/productos (opcionales)
    path('habitaciones/crear/', views.crear_habitacion, name='crear_habitacion'),
    path('habitaciones/<int:id>/editar/', views.actualizar_habitacion, name='actualizar_habitacion'),
    path('habitaciones/<int:id>/eliminar/', views.eliminar_habitacion, name='eliminar_habitacion'),
]