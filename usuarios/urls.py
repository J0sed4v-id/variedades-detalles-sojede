from django.urls import path, include
from . import views

urlpatterns = [


    path('', views.inicio, name='inicio'),  # Página principal
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar/', views.registrar, name='registrar'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'), 
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
    # Acceso desde dashboard
    path('productos/', views.listar_productos, name='productos'),
    path('inventario/', views.gestionar_inventario, name='inventario'),   # ajustar si necesitas otra vista
    path('compras/', views.gestionar_compras, name='compras'),       # ajustar si necesitas otra vista
    path('comprar_producto/<int:producto_id>/', views.comprar_producto, name='comprar_producto'),
    path('compras/pagar/<int:compra_id>/', views.pagar_compra, name='pagar_compra'),

    # CRUD de productos (opcionales)
    path('productos/', views.listar_productos, name='productos'),
    path('productos/guardar/', views.agregar_producto, name='agregar_producto'),
    # path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),







]