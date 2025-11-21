"""
Serializers para el Asistente de IA
"""
from rest_framework import serializers
from .models import Conversacion, Mensaje, ConsultaSQL


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'rol', 'contenido', 'metadata', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class ConversacionSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)
    ultimo_mensaje = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'fecha_creacion', 'fecha_actualizacion', 
                  'activa', 'mensajes', 'ultimo_mensaje']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_ultimo_mensaje(self, obj):
        ultimo = obj.mensajes.last()
        if ultimo:
            return {
                'contenido': ultimo.contenido[:100],
                'rol': ultimo.rol,
                'fecha': ultimo.fecha_creacion
            }
        return None


class ConversacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar conversaciones"""
    ultimo_mensaje = serializers.SerializerMethodField()
    cantidad_mensajes = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'fecha_creacion', 'fecha_actualizacion', 
                  'activa', 'ultimo_mensaje', 'cantidad_mensajes']
    
    def get_ultimo_mensaje(self, obj):
        ultimo = obj.mensajes.last()
        if ultimo:
            return {
                'contenido': ultimo.contenido[:100],
                'rol': ultimo.rol
            }
        return None
    
    def get_cantidad_mensajes(self, obj):
        return obj.mensajes.count()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer para requests de chat"""
    mensaje = serializers.CharField(required=True)
    conversacion_id = serializers.IntegerField(required=False, allow_null=True)
    nuevo_chat = serializers.BooleanField(default=False)


class ConsultaSQLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultaSQL
        fields = ['id', 'consulta', 'resultado', 'exitosa', 'error', 
                  'tiempo_ejecucion', 'fecha_ejecucion']
        read_only_fields = ['id', 'fecha_ejecucion']
