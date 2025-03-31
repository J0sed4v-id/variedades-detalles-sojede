from django.db import models
from django.contrib.auth.models import User

# Establecer opciones de estado de manera global
ESTADO_RESERVA_CHOICES = [
    ('confirmada', 'Confirmada'),
    ('pendiente', 'Pendiente'),
    ('cancelada', 'Cancelada'),
]

ESTADO_PAGO_CHOICES = [
    ('completado', 'Completado'),
    ('pendiente', 'Pendiente'),
]

METODO_PAGO_CHOICES = [
    ('tarjeta', 'Tarjeta'),
    ('efectivo', 'Efectivo'),
]

# Modelo Habitacion
class Habitacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Hacer el campo 'usuario' opcional
    capacidad = models.IntegerField()
    disponible = models.BooleanField(default=True)
    numero = models.CharField(max_length=10, unique=True)  # Garantiza que los números de habitación sean únicos
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20)
DISPONIBILIDAD_CHOICES = [
        ('disponible', 'Disponible'),
        ('no_disponible', 'No Disponible'),
    ]
estado = models.CharField(max_length=15, choices=DISPONIBILIDAD_CHOICES, default='disponible')
    

def __str__(self):
    return f"Habitación {self.numero} - {self.tipo}"

# Modelo Cliente
class Cliente(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_cliente

# Modelo Empleado
class Empleado(models.Model):
    nombre_empleado = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_empleado

# Modelo Reserva
class Reserva(models.Model):
    # Definimos los estados posibles de la reserva
    ESTADO_RESERVA_CHOICES = [
        ('reservada', 'Reservada'),
        ('cancelada', 'Cancelada'),
    ]
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado_reserva = models.CharField(max_length=15, choices=ESTADO_RESERVA_CHOICES)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    habitacion = models.ForeignKey('Habitacion', on_delete=models.SET_NULL, null=True, blank=True)  # Ahora es obligatorio
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.estado_reserva}"

# Modelo Pago
class Pago(models.Model):
    fecha_pago = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=10, choices=METODO_PAGO_CHOICES)
    estado_pago = models.CharField(max_length=15, choices=ESTADO_PAGO_CHOICES)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pago {self.id} - {self.estado_pago}"

# Modelo ServicioLavanderia
class ServicioLavanderia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relaciona el servicio con el usuario del sistema
    habitacion = models.ForeignKey('Habitacion', on_delete=models.SET_NULL, null=True) # Relaciona el servicio con una habitación
    fecha_solicitud = models.DateTimeField(auto_now_add=True)  # Fecha y hora de la solicitud
    estado = models.CharField(max_length=50, default='Pendiente')  # Estado del servicio (por defecto: Pendiente)
    descripcion = models.TextField(max_length=255)  # Detalles del servicio
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Costo del servicio

    def __str__(self):
        return f"Servicio #{self.id} - {self.habitacion.numero} - {self.estado}"
# Modelo ReservaServicio
class ReservaServicio(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    servicio_lavanderia = models.ForeignKey(ServicioLavanderia, on_delete=models.CASCADE)
    cantidad_servicios = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculamos el precio total automáticamente si existe el precio del servicio
        if self.servicio_lavanderia.precio_servicio is not None:
            self.precio_total = self.servicio_lavanderia.precio_servicio * self.cantidad_servicios
        else:
            self.precio_total = 0  # Si no tiene precio, fijamos el precio total en 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva Servicio {self.id}"

# Modelo Reporte
class Reporte(models.Model):
    fecha_generacion = models.DateField()
    tipo_reporte = models.CharField(max_length=50)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo_reporte}"
