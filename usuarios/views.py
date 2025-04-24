from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, BuscarHabitacionForm, HabitacionForm
from .models import Habitacion, ServicioLavanderia, Reserva, Cliente
from .forms import ReservaForm
from django.db import IntegrityError
from .forms import ReservaForm
# Vista para el dashboard (requiere que el usuario esté autenticado)
@login_required(login_url='iniciar_sesion')
def dashboard(request):
    return render(request, 'usuarios/dashboard.html')

# Vista para la página de inicio
def inicio(request):
    return render(request, 'usuarios/inicio.html')

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

# Vista para cerrar sesión
def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('inicio')

# Vista para buscar habitaciones disponibles
def buscar_habitaciones(request):
    form = BuscarHabitacionForm(request.POST or None)
    habitaciones_disponibles = None

    if request.method == 'POST' and form.is_valid():
        check_in = form.cleaned_data['check_in']
        check_out = form.cleaned_data['check_out']
        guests = form.cleaned_data['guests']

        if check_in < timezone.now().date():
            form.add_error('check_in', "La fecha de entrada no puede ser en el pasado.")
        elif check_out <= check_in:
            form.add_error('check_out', "La fecha de salida debe ser posterior a la de entrada.")
        else:
            habitaciones_disponibles = Habitacion.objects.filter(
                disponible=True,
                capacidad__gte=guests
            )

    return render(request, 'usuarios/buscar_habitaciones.html', {
        'form': form,
        'habitaciones_disponibles': habitaciones_disponibles
    })

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


# Vista para eliminar una habitación
def eliminar_habitacion(request, id):
    habitacion = get_object_or_404(Habitacion, id=id)

    # Eliminar los servicios de lavandería asociados
    try:
        ServicioLavanderia.objects.filter(habitacion=habitacion).delete()
    except IntegrityError as e:
        print(f"Error al eliminar los servicios de lavandería: {e}")

    # Eliminar la habitación
    habitacion.delete()
    return redirect('visualizar_habitaciones')


# Vista para visualizar todas las habitaciones
@login_required
def visualizar_habitaciones(request):
    habitaciones = Habitacion.objects.all()
    return render(request, 'usuarios/visualizar_habitaciones.html', {'habitaciones': habitaciones})


# Vista para reservar una habitación
@login_required
def reservar_habitacion(request):
     if request.method == 'POST':
        habitacion_id = request.POST.get('habitacion')
        fecha_inicio = request.POST.get('fecha_check_in')
        fecha_fin = request.POST.get('fecha_check_out')

        try:
            # Validar que la habitación exista
            habitacion = Habitacion.objects.get(id=habitacion_id)

            # Verificar si la habitación está disponible
            if habitacion.disponible:
                habitacion.disponible = False  # Cambiar el estado de la habitación
                habitacion.save()

                # Obtener o crear el cliente asociado al usuario
                cliente, created = Cliente.objects.get_or_create(usuario=request.user)

                # Crear la reserva
                reserva = Reserva.objects.create(
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado_reserva='reservada',
                    habitacion=habitacion,
                    cliente=cliente
                )

                # Notificar éxito
                messages.success(request, f'¡Reserva realizada con éxito! La habitación {habitacion.numero} está ahora reservada.')
            else:
                messages.error(request, 'La habitación seleccionada no está disponible.')

        except Habitacion.DoesNotExist:
            messages.error(request, 'La habitación seleccionada no existe o no es válida.')
        except Exception as e:
            # Manejar otros errores inesperados
            messages.error(request, f'Ocurrió un error al realizar la reserva: {str(e)}')

        # Redirigir siempre al dashboard después del intento de reserva
        return redirect('dashboard')

    # Obtener habitaciones disponibles para la plantilla
     habitaciones_disponibles = Habitacion.objects.filter(disponible=True)
     return render(request, 'usuarios/reservar_habitacion.html', {'habitaciones_disponibles': habitaciones_disponibles})


# Vista para solicitar un servicio (lavandería)
@login_required
def solicitar_servicio(request):
    # Filtrar las habitaciones del usuario autenticado
    habitaciones = Habitacion.objects.filter(usuario=request.user)

    # Si el usuario no tiene habitaciones registradas, redirigirlo a la creación de habitación
    if not habitaciones.exists():
        messages.info(request, "No tienes habitaciones registradas. Por favor, crea una habitación antes de solicitar un servicio.")
        return redirect('crear_habitacion')

    # Manejar la solicitud POST para registrar el servicio
    if request.method == 'POST':
        habitacion_id = request.POST.get('habitacion')
        descripcion = request.POST.get('descripcion', '').strip()
        precio_servicio = request.POST.get('precio_servicio', 0)

        try:
            # Obtener la habitación seleccionada
            habitacion = Habitacion.objects.get(id=habitacion_id, usuario=request.user)
            # Crear un nuevo servicio de lavandería
            ServicioLavanderia.objects.create(
                usuario=request.user,
                habitacion=habitacion,
                descripcion=descripcion,
                precio_servicio=precio_servicio,
            )
            messages.success(request, f"Servicio de lavandería registrado exitosamente para la habitación {habitacion.numero}.")
            return redirect('visualizar_habitaciones')
        except Habitacion.DoesNotExist:
            messages.error(request, "La habitación seleccionada no es válida.")

    # Renderizar la plantilla de solicitar servicio con las habitaciones del usuario
    return render(request, 'usuarios/solicitar_servicio.html', {'habitaciones': habitaciones})
@login_required
def visualizar_facturas(request):
    # Lógica para obtener las facturas del usuario
    facturas = []  # Aquí deberías obtener las facturas relacionadas con el usuario
    return render(request, 'usuarios/visualizar_facturas.html', {'facturas': facturas})

# Vista para modificar una reserva
@login_required
def modificar_reserva(request, id):
    # Aquí deberías obtener la reserva según el 'id' y permitir que el usuario la modifique
    reserva = get_object_or_404(Habitacion, id=id, usuario=request.user)  # Asumiendo que las reservas están relacionadas con habitaciones
    
    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, "Reserva modificada con éxito.")
            return redirect('visualizar_habitaciones')
    else:
        form = HabitacionForm(instance=reserva)
    
    return render(request, 'usuarios/modificar_reserva.html', {'form': form})



# Vista para cancelar una reserva
@login_required(login_url='iniciar_sesion')
def cancelar_reserva(request):
    # Solo obtener las reservas con estado 'reservada' y asociadas a una habitación no disponible.
    if request.method == 'POST':
        habitacion_id = request.POST.get('habitacion_id')
        
        try:
            # Filtrar las reservas con estado 'reservada' y asociadas a la habitación que se seleccionó
            reservas = Reserva.objects.filter(habitacion_id=habitacion_id, estado_reserva='reservada')

            if reservas.count() == 1:
                reserva = reservas.first()

                # Cancelar la reserva
                reserva.estado_reserva = 'cancelada'
                reserva.habitacion.disponible = True  # Hacer disponible la habitación
                reserva.habitacion.save()
                reserva.save()

                # Notificar al usuario
                messages.success(request, f'¡Reserva para la habitación {reserva.habitacion.numero} cancelada con éxito!')
            else:
                messages.error(request, 'No se encontró una reserva válida para cancelar.')

        except Exception as e:
            messages.error(request, f'Ocurrió un error: {str(e)}')

        return redirect('dashboard')

    # Si no es un POST, filtrar las habitaciones reservadas para mostrarlas en el formulario
    habitaciones_reservadas = Habitacion.objects.filter(disponible=False)
    
    return render(request, 'usuarios/cancelar_reserva.html', {'habitaciones_reservadas': habitaciones_reservadas})


# Vista para generar una factura
@login_required(login_url='iniciar_sesion')
def generar_factura(request):
    # Aquí se agregarán las funcionalidades para generar una factura
    messages.info(request, "Funcionalidad para generar una factura aún no implementada.")
    return render(request, 'usuarios/generar_factura.html')

# Vista para generar un pago
@login_required(login_url='iniciar_sesion')
def generar_pago(request):
    # Aquí se agregarán las funcionalidades para generar un pago
    messages.info(request, "Funcionalidad para generar un pago aún no implementada.")
    return render(request, 'usuarios/generar_pago.html')

# Vista para notificar un servicio
@login_required(login_url='iniciar_sesion')
def notificar_servicio(request):
    # Aquí se agregarán las funcionalidades para notificar un servicio
    messages.info(request, "Funcionalidad para notificar un servicio aún no implementada.")
    return render(request, 'usuarios/notificar_servicio.html')

# Vista para generar un informe de ingresos
@login_required(login_url='iniciar_sesion')
def generar_informe_ingresos(request):
    # Aquí se agregarán las funcionalidades para generar un informe de ingresos
    messages.info(request, "Funcionalidad para generar un informe de ingresos aún no implementada.")
    return render(request, 'usuarios/generar_informe_ingresos.html')

# Vista para solicitar un servicio (lavandería u otros)
@login_required(login_url='iniciar_sesion')
def solicitar_servicio(request):
    # Aquí se agregarán las funcionalidades para solicitar un servicio
    messages.info(request, "Funcionalidad para solicitar un servicio aún no implementada.")
    return render(request, 'usuarios/solicitar_servicio.html')