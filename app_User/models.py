from django.db import models
from app_Empresa.models import Empresa
from django.contrib.auth.models import User, Group

class Perfiluser(models.Model):
    imagen_url = models.URLField(
        max_length=200,
        blank=True,
        null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.empresa.razon_social}"


class GroupDescripcion(models.Model):
    """Modelo para almacenar la descripción de los grupos y asociarlos a una empresa (multitenancy)"""
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='descripcion_obj')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='grupos', null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        empresa_name = self.empresa.razon_social if self.empresa else "Sin empresa"
        return f"{self.group.name} - {empresa_name}"
