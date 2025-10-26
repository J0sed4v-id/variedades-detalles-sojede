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
    path('compras/', views.gestionar_compras, name='compras'),
    path('comprar_producto/<int:producto_id>/', views.comprar_producto, name='comprar_producto'),
    path('compras/pagar/<int:compra_id>/', views.pagar_compra, name='pagar_compra'),

    # CRUD de productos
    path('productos/guardar/', views.agregar_producto, name='agregar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # Nueva ruta para autocompletado
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
]
