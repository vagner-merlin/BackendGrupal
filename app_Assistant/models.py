"""
Modelos para el Asistente de IA
"""
from django.db import models
from django.contrib.auth.models import User
from app_Empresa.models import Empresa


class Conversacion(models.Model):
    """Historial de conversaciones con el asistente"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='conversaciones')
    titulo = models.CharField(max_length=255, default="Nueva conversación")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'assistant_conversacion'
        ordering = ['-fecha_actualizacion']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"


class Mensaje(models.Model):
    """Mensajes individuales en una conversación"""
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]
    
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    rol = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenido = models.TextField()
    metadata = models.JSONField(null=True, blank=True)  # Para datos adicionales, consultas SQL, etc.
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assistant_mensaje'
        ordering = ['fecha_creacion']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
    
    def __str__(self):
        return f"{self.rol}: {self.contenido[:50]}..."


class ConsultaSQL(models.Model):
    """Registro de consultas SQL ejecutadas"""
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE, related_name='consultas_sql', null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    consulta = models.TextField()
    resultado = models.JSONField(null=True, blank=True)
    exitosa = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)
    tiempo_ejecucion = models.FloatField(null=True, blank=True)  # En segundos
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assistant_consulta_sql'
        ordering = ['-fecha_ejecucion']
        verbose_name = 'Consulta SQL'
        verbose_name_plural = 'Consultas SQL'
    
    def __str__(self):
        status = "✓" if self.exitosa else "✗"
        return f"{status} {self.consulta[:50]}..."

