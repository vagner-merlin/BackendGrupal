from django.db import models
from django.contrib.auth.models import User
from app_Cliente.models import Cliente
from app_User.models import Perfiluser
from app_Empresa.models import Empresa

# Create your models here.
ENUM_ESTADO_CREDITO = [
    ('Pendiente', 'Pendiente'),
    ('Aprobado', 'Aprobado'),
    ('Rechazado', 'Rechazado'),
    ('SOLICITADO', 'SOLICITADO'),
    ('DESENBOLSADO', 'DESENBOLSADO'),
    ('FINALIZADO', 'FINALIZADO'),
]

ENUM_FASE_CREDITO = [
    ('FASE_1_SOLICITUD', 'Datos de la solicitud'),
    ('FASE_2_DOCUMENTACION', 'Documentación personal'),
    ('FASE_3_LABORAL', 'Información laboral'),
    ('FASE_4_DOMICILIO', 'Domicilio'),
    ('FASE_5_GARANTE', 'Datos del garante'),
    ('FASE_6_REVISION', 'Revisión y aprobación'),
    ('FASE_7_DESEMBOLSO', 'Desembolso del crédito'),
    ('FASE_8_FINALIZADO', 'Crédito finalizado'),
]

class Tipo_Credito(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    monto_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    monto_maximo = models.DecimalField(max_digits=10, decimal_places=2)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre
    

class Credito(models.Model): 
    Monto_Solicitado = models.DecimalField(max_digits=10, decimal_places=2)
    enum_estado = models.CharField(max_length=20, choices=ENUM_ESTADO_CREDITO, default='SOLICITADO')
    fase_actual = models.CharField(max_length=30, choices=ENUM_FASE_CREDITO, default='FASE_1_SOLICITUD')
    Numero_Cuotas = models.IntegerField()
    Monto_Cuota = models.DecimalField(max_digits=10, decimal_places=2)
    Moneda = models.CharField(max_length=10, default='USD')
    Tasa_Interes = models.DecimalField(max_digits=5, decimal_places=2)
    Fecha_Aprobacion = models.DateField(null=True, blank=True)
    Fecha_Desembolso = models.DateField(null=True, blank=True)
    Fecha_Finalizacion = models.DateField(null=True, blank=True)
    Monto_Pagar = models.DecimalField(max_digits=10, decimal_places=2)
    razon_rechazo = models.TextField(null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_credito = models.ForeignKey(Tipo_Credito, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Crédito {self.id} - Cliente: {self.cliente.nombre} - Monto Solicitado: {self.Monto_Solicitado} {self.Moneda}"
    
    
class HistoricoCredito(models.Model):
    """Registra el historial de cambios de fase en cada crédito"""
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name='historico')
    fase_anterior = models.CharField(max_length=30, choices=ENUM_FASE_CREDITO, null=True, blank=True)
    fase_nueva = models.CharField(max_length=30, choices=ENUM_FASE_CREDITO)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_cambio = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    datos_agregados = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"Crédito {self.credito.id} - {self.fase_anterior} → {self.fase_nueva} - {self.fecha_cambio}"
    
class Ganancia_Credito(models.Model):
    monto_prestado = models.DecimalField(max_digits=10, decimal_places=2)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2)
    duracion_meses = models.IntegerField()
    ganacia_esperada = models.DecimalField(max_digits=10, decimal_places=2)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    Credito = models.ForeignKey(Credito, on_delete=models.CASCADE)

    def __str__(self):
        return f"Ganancia Crédito {self.Credito.id} - Cliente: {self.Cliente.nombre}"
       


