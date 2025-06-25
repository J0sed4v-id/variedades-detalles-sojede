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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    capacidad = models.IntegerField()
    disponible = models.BooleanField(default=True)
    numero = models.CharField(max_length=10, unique=True)
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


# Modelo Reporte
class Reporte(models.Model):
    fecha_generacion = models.DateField()
    tipo_reporte = models.CharField(max_length=50)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo_reporte}"
    
#Modelo factura
class Factura(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    noches = models.PositiveIntegerField()
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False)

    class Meta:
        db_table = 'usuarios_factura'  # <== esto hace que la tabla se llame así en SQLite

    def __str__(self):
        return f"Factura de {self.usuario.username} - Reserva {self.reserva.id}"

