from django.db import models
from app_Empresa.models import Empresa

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    fecha_registro = models.DateField(auto_now_add=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='clientes', null=True, blank=True)

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Documentacion(models.Model):
    ci = models.CharField(max_length=20, unique=True)
    documento_url = models.URLField(max_length=200)
    fecha_registro = models.DateField(auto_now_add=True)
    id_cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE, null=True, related_name='documentacion')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='documentaciones', null=True, blank=True)

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Doc: {self.ci}"

class Trabajo(models.Model):
    cargo = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)
    extracto_url = models.URLField(max_length=200)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    ubicacion = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    id_cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE, null=True)
    empresa_rel = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.cargo} en {self.empresa}"

class Domicilio(models.Model):
    descripcion = models.CharField(max_length=200)
    croquis_url = models.URLField(max_length=200)
    es_propietario = models.BooleanField()
    numero_ref = models.CharField(max_length=50)
    id_cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Domicilio: {self.numero_ref}"

class Garante(models.Model):
    nombrecompleto = models.CharField(max_length=100)
    ci = models.CharField(max_length=20)
    telefono = models.CharField(max_length=15)
    id_domicilio = models.OneToOneField('Domicilio', on_delete=models.CASCADE, null=True, related_name='garante')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='garantess', null=True, blank=True)

    def __str__(self):
        return self.nombrecompleto
