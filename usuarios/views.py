from datetime import date
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Sum, Q  # Importación necesaria para consultas complejas
from django.template.loader import get_template

from .forms import CustomUserCreationForm, ReservaForm
from .models import Reserva, Cliente, Factura, Compra, Producto, Venta, DetalleVenta

from xhtml2pdf import pisa
import io


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


#/////////////////////////////////////////////////////////////////////////////////////

# Vista para visualizar todas las habitaciones
@login_required
def gestionar_productos(request):
    productos = Producto.objects.all()
    form = ProductoForm()

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos')

    return render(request, 'usuarios/productos.html', {
        'productos': productos,
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
        precio = request.POST.get("precio")
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
            producto.precio = precio
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
                precio=precio,
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

# Vista para gestionar compras con formulario moderno
@login_required
def gestionar_compras(request):
    usuario = request.user
    cliente, _ = Cliente.objects.get_or_create(usuario=usuario)

    # 🔸 Categorías únicas para el select
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()

    # 🧾 Historial de compras del cliente
    compras = Compra.objects.filter(cliente=cliente).select_related('producto').order_by('-fecha_compra')

    # 🛒 Registrar nueva compra
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad'))
        total = request.POST.get('total')

        producto = get_object_or_404(Producto, id=producto_id)

        if producto.stock < cantidad:
            messages.error(request, f"❌ Stock insuficiente para '{producto.nombre}'.")
            return redirect('compras')

        # Actualizar stock
        producto.stock -= cantidad
        producto.save()

        # Crear compra
        Compra.objects.create(
            cliente=cliente,
            producto=producto,
            cantidad=cantidad,
            total=total
        )

        messages.success(request, f"✅ Compra registrada: {cantidad} x '{producto.nombre}'.")
        return redirect('compras')

    # 🔁 Renderizar plantilla con datos
    return render(request, 'usuarios/compras.html', {
        'categorias': categorias,
        'compras': compras
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
    producto = get_object_or_404(Producto, id=producto_id)

    # Verificar que haya stock disponible
    if producto.stock <= 0:
        messages.error(request, f"❌ El producto '{producto.nombre}' no tiene stock disponible.")
        return redirect('compras')

    # Cantidad comprada (por ahora asumimos 1 unidad)
    cantidad = 1

    # Restar del inventario
    producto.stock -= cantidad
    producto.save()

    # Mostrar mensaje de confirmación
    messages.success(request, f"✅ Has comprado '{producto.nombre}'. Stock restante: {producto.stock}.")

    return redirect('compras')



@login_required
def generar_factura_pdf(request, venta_id):
    """Genera una factura térmica en PDF basada en una venta."""
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    template_path = 'usuarios/factura_venta.html'
    context = {
        'venta': venta,
        'detalles': detalles,
        'user': request.user
    }

    # Renderizar el template HTML a PDF
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="factura_{venta.id}.pdf"'

    # Crear el PDF con xhtml2pdf
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('UTF-8')), dest=response, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response


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
    
    return render(request, 'usuarios/inventario.html', context)


@login_required
def registrar_venta(request):
    ventas = Venta.objects.order_by('-fecha')
    return render(request, 'usuarios/registrar_venta.html', {'ventas': ventas})

@login_required
def buscar_producto_por_codigo(request):
    codigo = request.GET.get('codigo', None)
    data = {'error': 'Producto no encontrado.'}
    if codigo:
        try:
            producto = Producto.objects.get(codigo=codigo)
            data = {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': producto.precio,
                'stock': producto.stock,
                'codigo': producto.codigo
            }
        except Producto.DoesNotExist:
            pass
    return JsonResponse(data)

@login_required
def guardar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productos = data.get('productos', [])
            totales = data.get('totales', {})

            # Crear la venta
            venta = Venta.objects.create(
                subtotal=totales.get('subtotal'),
                iva=totales.get('iva'),
                total=totales.get('total'),
                cajero=request.user.username,
                vendedor=request.user.username,
                caja='1'  # Valor por defecto
            )

            # Crear los detalles y actualizar stock
            for item in productos:
                producto = get_object_or_404(Producto, id=item['id'])
                cantidad = int(item['cantidad'])
                
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=item['precio'],
                    subtotal=item['subtotal']
                )
                
                # Actualizar stock
                producto.stock -= cantidad
                producto.save()

            # Generar la URL del PDF para la respuesta
            pdf_url = reverse('generar_factura_pdf', args=[venta.id])

            # Respuesta con URL del PDF incluida
            return JsonResponse({
                'status': 'success',
                'venta_id': venta.id,
                'pdf_url': pdf_url
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



@login_required
def listar_todos_los_productos_api(request):
    """Devuelve una lista de todos los productos para el modal de búsqueda."""
    productos = Producto.objects.all().values('id', 'codigo', 'nombre', 'precio', 'stock')
    return JsonResponse(list(productos), safe=False)


@login_required
def get_product_details(request, producto_id):
    """Devuelve el precio, stock y categoría de un producto en formato JSON."""
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        data = {
            'precio': producto.precio,
            'stock': producto.stock,
            'categoria': producto.categoria,
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


@login_required
def buscar_productos(request):
    """Devuelve productos que coinciden con la búsqueda (para el autocompletado)."""
    termino = request.GET.get("q", "")
    resultados = (
        Producto.objects.filter(nombre__icontains=termino)
        .order_by("nombre")[:10]
    )
    data = [{"id": p.id, "text": f"{p.nombre} — Stock: {p.stock}"} for p in resultados]
    return JsonResponse({"results": data})
