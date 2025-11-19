from django.db import models

ENUM_TEMAS = [
    ('CLARO', 'Claro'),
    ('OSCURO', 'Oscuro'),
    ('AUTOMATICO', 'Automatico'),
]
ENUM_PLANES = [
    ('BASICO', 'Básico'),
    ('PREMIUM', 'Premium'),
    ('EMPRESARIAL', 'Empresarial'),
]
ENUM_ESTADOS = [
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
    ('SUSPENDIDO', 'Suspendido'),
]

class Empresa(models.Model):
    razon_social = models.CharField(max_length=255)
    email_contacto = models.EmailField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    nombre_comercial = models.CharField(max_length=255, blank=True, null=True)
    Imagen_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.razon_social

class Configuracion(models.Model):
    color = models.CharField(max_length=7)  
    tipo_letra = models.CharField(max_length=100)
    enum_tema = models.CharField(max_length=10, choices=ENUM_TEMAS, default='CLARO')
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)
    

class Suscripcion(models.Model):
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField()
    activo = models.BooleanField(default=True)
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)
    enum_plan = models.CharField(max_length=15, choices=ENUM_PLANES, default='BASICO')
    enum_estado = models.CharField(max_length=15, choices=ENUM_ESTADOS, default='ACTIVO')

class PagoSuscripcion(models.Model):
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_proximo_pago = models.DateTimeField()
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE)

class on_premise(models.Model):
    razon_social = models.CharField(max_length=255)
    email_contacto = models.EmailField()
    version = models.CharField(max_length=50)
    fecha_instalacion = models.DateTimeField(auto_now_add=True)
    fecha_de_compra = models.DateTimeField(auto_now_add=True)
    fecha_sin_soporte = models.DateTimeField()