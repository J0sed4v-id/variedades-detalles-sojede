from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, BuscarHabitacionForm, HabitacionForm
from .models import Habitacion, Reserva, Cliente, Factura
from .forms import ReservaForm
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from .models import Producto
from django.db.models import Q

# Vista para el dashboard (requiere que el usuario esté autenticado)
@login_required(login_url='iniciar_sesion')
def dashboard(request):
    return render(request, 'usuarios/dashboard.html')
#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para la página de inicio
def inicio(request):
    return render(request, 'usuarios/inicio.html')
#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para el registro de usuarios
def registrar(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada con éxito. Ahora puedes iniciar sesión.")
            return redirect('inicio')
        else:
            messages.error(request, "Error en el registro. Revisa los campos.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/registro.html', {'form': form})
#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para iniciar sesión
def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect('dashboard')
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    return render(request, 'usuarios/inicio.html')
#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para cerrar sesión
def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('inicio')


#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para buscar habitaciones disponibles
def buscar_habitaciones(request):
    form = BuscarHabitacionForm(request.POST or None)
    habitaciones_disponibles = None

    if request.method == 'POST' and form.is_valid():
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']
       

        if check_in < timezone.now().date():
            form.add_error('check_in', "La fecha de entrada no puede ser en el pasado.")
        elif check_out <= check_in:
            form.add_error('check_out', "La fecha de salida debe ser posterior a la de entrada.")
        else:
            habitaciones_disponibles = Habitacion.objects.filter(
                disponible=True,
            )

    return render(request, 'usuarios/buscar_habitaciones.html', {
        'form': form,
        'habitaciones_disponibles': habitaciones_disponibles
    })
#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para crear una nueva habitación
@login_required
def crear_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            habitacion = form.save(commit=False)
            habitacion.usuario = request.user  # Asignar el usuario autenticado
            habitacion.save()
            messages.success(request, "Habitación creada con éxito.")
            return redirect('visualizar_habitaciones')
    else:
        form = HabitacionForm()
    return render(request, 'usuarios/crear_habitacion.html', {'form': form})
#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para actualizar los detalles de una habitación
@login_required
def actualizar_habitacion(request, id):
    habitacion = get_object_or_404(Habitacion, id=id)  # Eliminamos la restricción de usuario
    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Habitación actualizada con éxito.")
            return redirect('visualizar_habitaciones')
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'usuarios/actualizar_habitacion.html', {'form': form})

#/////////////////////////////////////////////////////////////////////////////////////////////////
# Vista para eliminar una habitación
def eliminar_habitacion(request, id):
    habitacion = get_object_or_404(Habitacion, id=id)

    # Eliminar la habitación
    habitacion.delete()
    return redirect('visualizar_habitaciones')






#/////////////////////////////////////////////////////////////////////////////////////

# Vista para visualizar todas las habitaciones
@login_required
def gestionar_productos(request):
    # gestión principal de "productos" reutilizando el modelo Habitacion
    habitaciones = Habitacion.objects.all()
    form = HabitacionForm()

    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos')

    return render(request, 'usuarios/productos.html', {
        'habitaciones': habitaciones,
        'form': form
    })



#/////////////////////////////////////////////////////////////////////////////////////

#vista del crud 
# ------------------ CRUD PRODUCTOS ------------------

@login_required
def listar_productos(request):
    query = request.GET.get('q')
    productos = Producto.objects.all()

    if query:
        productos = productos.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(categoria__icontains=query) |
            Q(id__icontains=query)
        )

    return render(request, 'usuarios/productos.html', {
        'productos': productos,
        'query': query
    })

#//////////////////////////////////////////////////////////////////////////////////////
@login_required
def agregar_producto(request):
    if request.method == "POST":
        id_producto = request.POST.get("id")  # Campo oculto del formulario
        codigo = request.POST.get("codigo")
        nombre = request.POST.get("nombre")
        stock = request.POST.get("stock")
        categoria = request.POST.get("categoria")

        if id_producto:  # Editar producto existente
            producto = get_object_or_404(Producto, id=id_producto)

            # Evitar duplicado de código
            if Producto.objects.filter(codigo=codigo).exclude(id=id_producto).exists():
                messages.error(request, f"⚠️ Ya existe un producto con el código {codigo}.")
                return redirect('productos')

            producto.codigo = codigo
            producto.nombre = nombre
            producto.stock = stock
            producto.categoria = categoria
            producto.save()
            messages.success(request, f"✅ Producto '{producto.nombre}' actualizado correctamente.")

        else:  # Crear nuevo producto
            if Producto.objects.filter(codigo=codigo).exists():
                messages.error(request, f"⚠️ El producto con código {codigo} ya existe.")
                return redirect('productos')

            Producto.objects.create(
                codigo=codigo,
                nombre=nombre,
                stock=stock,
                categoria=categoria
            )
            messages.success(request, "✅ Producto guardado exitosamente.")

        return redirect('productos')

    # Si no es POST, mostramos la lista
    productos = Producto.objects.all()
    return render(request, 'usuarios/productos.html', {'productos': productos})


@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('productos')

#//////////////////////////////////////////////////////////////////////////////////////////


#vista para gestionar compras (visualizar productos y historial de compras)
@login_required
def gestionar_compras(request):
    usuario = request.user
    cliente, _ = Cliente.objects.get_or_create(usuario=usuario)
    
    # Productos disponibles
    productos = Habitacion.objects.filter(disponible=True)
    
    # Historial de compras del cliente
    compras = Reserva.objects.filter(cliente=cliente).order_by('-id')
    paginator = Paginator(compras, 10)
    page_number = request.GET.get('page')
    compras_paginadas = paginator.get_page(page_number)
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = Habitacion.objects.get(id=producto_id)
        
        # Crear una "compra" usando Reserva como base
        compra = Reserva.objects.create(
            cliente=cliente,
            habitacion=producto,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),  # se puede ajustar según la lógica de la compra
            estado_reserva='comprada'  # nuevo estado para compras
        )
        
        messages.success(request, f'Has comprado el producto {producto.numero} correctamente.')
        return redirect('compras')
    
    return render(request, 'usuarios/compras.html', {
        'productos': productos,
        'compras': compras_paginadas
    })


# Vista para pagar una compra
@login_required
def pagar_compra(request, compra_id):
    compra = get_object_or_404(Reserva, id=compra_id, cliente__usuario=request.user, estado_reserva='comprada')
    compra.pagada = True  # asegúrate de tener este campo en Reserva o en Factura
    compra.save()
    messages.success(request, f'Compra del producto {compra.habitacion.numero} pagada correctamente.')
    return redirect('compras')

# Vista para comprar un producto
@login_required
def comprar_producto(request, producto_id):
    usuario = request.user
    cliente, _ = Cliente.objects.get_or_create(usuario=usuario)
    producto = get_object_or_404(Habitacion, id=producto_id)

    # Crear la compra (usaremos Reserva como compra temporal)
    reserva = Reserva.objects.create(
        cliente=cliente,
        habitacion=producto,
        fecha_inicio=timezone.now(),
        fecha_fin=timezone.now(),  # opcional, si no hay fecha de salida
        estado_reserva='reservada'  # temporal, podemos usarlo como 'pendiente pago'
    )

    messages.success(request, f'Has comprado el producto {producto.numero} correctamente.')
    return redirect('compras')























@login_required
def gestionar_reservas(request):
    usuario = request.user
    cliente, _ = Cliente.objects.get_or_create(usuario=usuario)
    reservas = Reserva.objects.filter(cliente=cliente, estado_reserva='reservada')
    habitaciones_disponibles = Habitacion.objects.filter(disponible=True)

    # --------------------- RESERVAR ---------------------
    if request.method == 'POST' and 'reservar' in request.POST:
        form = ReservaForm(request.POST)
        form.fields['habitacion'].queryset = habitaciones_disponibles  # Filtrar habitaciones disponibles
        if form.is_valid():
            reserva = form.save(commit=False)
            habitacion = reserva.habitacion
            if habitacion.disponible:
                habitacion.disponible = False
                habitacion.save()
                reserva.cliente = cliente
                reserva.estado_reserva = 'reservada'
                reserva.save()
                messages.success(request, f'¡Reserva realizada con éxito para la habitación {habitacion.numero}!')
                return redirect('gestionar_reservas')
            else:
                messages.error(request, 'La habitación seleccionada no está disponible.')
        else:
            messages.error(request, 'Hay errores en el formulario. Por favor verifica los datos.')

    # --------------------- CANCELAR ---------------------
    elif request.method == 'POST' and 'cancelar' in request.POST:
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=cliente, estado_reserva='reservada')
        reserva.estado_reserva = 'cancelada'
        reserva.habitacion.disponible = True
        reserva.habitacion.save()
        reserva.save()
        messages.success(request, f'Reserva para habitación {reserva.habitacion.numero} cancelada con éxito.')
        return redirect('gestionar_reservas')

    # ---------------------- MODIFICAR ------------------------
    elif request.method == 'POST' and 'modificar' in request.POST:
        reserva_id = request.POST.get('reserva_id_modificar')
        nueva_inicio = request.POST.get('nueva_fecha_inicio')
        nueva_fin = request.POST.get('nueva_fecha_fin')

        try:
            reserva = Reserva.objects.get(id=reserva_id, cliente=cliente, estado_reserva='reservada')
            reserva.fecha_inicio = nueva_inicio
            reserva.fecha_fin = nueva_fin
            reserva.save()
            messages.success(request, f'Reserva {reserva.id} modificada con éxito.')
        except Reserva.DoesNotExist:
            messages.error(request, 'Reserva no encontrada para modificar.')
        return redirect('gestionar_reservas')

    else:
        form = ReservaForm()

    context = {
        'form': form,
        'reservas': reservas,
        'habitaciones_disponibles': habitaciones_disponibles,
        'hoy': date.today()
    }
    return render(request, 'usuarios/gestionar_reservas.html', context)

# _ _ _ _ _

@login_required
def visualizar_facturas(request):
    cliente = Cliente.objects.filter(usuario=request.user).first()

    if not cliente:
        messages.error(request, "Tu usuario no está asociado a un cliente.")
        return redirect('dashboard')

    facturas_qs = Factura.objects.filter(usuario=request.user).select_related('reserva__habitacion').order_by('-id')

    # Paginación
    paginator = Paginator(facturas_qs, 10)  # 10 facturas por página
    page_number = request.GET.get('page')
    facturas_paginadas = paginator.get_page(page_number)

    return render(request, 'usuarios/visualizar_facturas.html', {
        'facturas': facturas_paginadas
    })


# Vista para generar una factura
@login_required(login_url='iniciar_sesion')
def generar_factura(request):
    cliente = Cliente.objects.filter(usuario=request.user).first()

    if not cliente:
        messages.error(request, "Tu usuario no está asociado a ningún cliente.")
        return redirect('dashboard')

    reserva_id = request.GET.get("reserva_id")

    if reserva_id:
        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=cliente)

        noches = (reserva.fecha_fin - reserva.fecha_inicio).days
        precio_noche = reserva.habitacion.precio_por_noche if reserva.habitacion else 0
        total = noches * precio_noche

        factura, creada = Factura.objects.get_or_create(
            reserva=reserva,
            defaults={
                'usuario': cliente.usuario,
                'noches': noches,
                'precio_por_noche': precio_noche,
                'total': total,
            }
        )

        return render(request, 'usuarios/generar_factura.html', {
            'reserva_seleccionada': reserva,
            'noches': noches,
            'precio_noche': precio_noche,
            'total': total,
        })

    reservas = Reserva.objects.filter(cliente=cliente, estado_reserva='reservada')

    return render(request, 'usuarios/generar_factura.html', {
        'reservas': reservas,
    })


# Vista para generar un informe de ingresos
@login_required(login_url='iniciar_sesion')
def generar_informe_ingresos(request):
    total_ingresos = None
    facturas_filtradas = []

    if request.method == 'POST':
        fecha_inicio = request.POST.get('start-date')
        fecha_fin = request.POST.get('end-date')

        if fecha_inicio and fecha_fin:
            facturas_filtradas = Factura.objects.filter(
                reserva__fecha_inicio__gte=fecha_inicio,
                reserva__fecha_fin__lte=fecha_fin
            )
            total_ingresos = facturas_filtradas.aggregate(Sum('total'))['total__sum'] or 0
        else:
            messages.error(request, "Por favor selecciona ambas fechas.")

    return render(request, 'usuarios/generar_informe_ingresos.html', {
        'facturas': facturas_filtradas,
        'total_ingresos': total_ingresos
    })



@require_POST
@login_required
def pagar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    # Lógica básica de pago: marcar como pagada
    factura.pagada = True  # Asegúrate de tener este campo en el modelo Factura
    factura.save()
    messages.success(request, "Factura pagada correctamente.")
    return redirect('visualizar_facturas')


@login_required
def gestionar_inventario(request):
    # Obtener parámetros de búsqueda y filtrado
    search_query = request.GET.get('search', '')
    categoria_filter = request.GET.get('categoria', '')
    
    # Consultar productos
    productos = Producto.objects.all()
    
    # Aplicar búsqueda
    if search_query:
        productos = productos.filter(
            models.Q(nombre__icontains=search_query) |
            models.Q(codigo__icontains=search_query)
        )
    
    # Aplicar filtro por categoría
    if categoria_filter:
        productos = productos.filter(categoria=categoria_filter)
    
    # Obtener categorías únicas para el filtro
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    # Determinar el estado del stock
    for producto in productos:
        if producto.stock == 0:
            producto.estado = 'empty'
        elif producto.stock < 10:  # Puedes ajustar este valor según tus necesidades
            producto.estado = 'low'
        else:
            producto.estado = 'ok'
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'search_query': search_query,
        'categoria_selected': categoria_filter
    }
    
    return render(request, 'inventario.html', context)
