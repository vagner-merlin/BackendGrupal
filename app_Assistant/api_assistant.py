"""
API Views para el Asistente de IA
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from app_User.models import Perfiluser
from .models import Conversacion, Mensaje
from .serializers import (
    ConversacionSerializer, ConversacionListSerializer,
    MensajeSerializer, ChatRequestSerializer
)
from .groq_service import groq_service


class AssistantViewSet(viewsets.ViewSet):
    """ViewSet para el asistente de IA"""
    permission_classes = [IsAuthenticated]
    
    def get_perfil_and_empresa(self, user):
        """Obtiene perfil y empresa del usuario"""
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return perfil, perfil.empresa
        except Perfiluser.DoesNotExist:
            return None, None
    
    @action(detail=False, methods=['post'], url_path='chat')
    def chat(self, request):
        """
        Endpoint principal para chatear con el asistente
        POST /api/assistant/chat/
        Body: {
            "mensaje": "¿Cuántos clientes tengo?",
            "conversacion_id": 1,  // Opcional
            "nuevo_chat": false     // Si es true, crea nueva conversación
        }
        """
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        perfil, empresa = self.get_perfil_and_empresa(request.user)
        if not perfil or not empresa:
            return Response(
                {"error": "Usuario no tiene perfil o empresa asociada"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        mensaje_texto = serializer.validated_data['mensaje']
        conversacion_id = serializer.validated_data.get('conversacion_id')
        nuevo_chat = serializer.validated_data.get('nuevo_chat', False)
        
        # Obtener o crear conversación
        if nuevo_chat or not conversacion_id:
            conversacion = Conversacion.objects.create(
                usuario=request.user,
                empresa=empresa,
                titulo=mensaje_texto[:100]  # Usar primeros 100 chars como título
            )
        else:
            try:
                conversacion = Conversacion.objects.get(
                    id=conversacion_id,
                    usuario=request.user,
                    empresa=empresa
                )
            except Conversacion.DoesNotExist:
                return Response(
                    {"error": "Conversación no encontrada"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Guardar mensaje del usuario
        mensaje_usuario = Mensaje.objects.create(
            conversacion=conversacion,
            rol='user',
            contenido=mensaje_texto
        )
        
        # Obtener historial de la conversación
        mensajes_previos = conversacion.mensajes.exclude(id=mensaje_usuario.id).order_by('fecha_creacion')
        historial = [
            {"role": msg.rol, "content": msg.contenido}
            for msg in mensajes_previos
        ]
        
        # Procesar con Groq
        try:
            respuesta, messages_log = groq_service.process_message(
                mensaje_texto,
                historial,
                request.user,
                empresa
            )
            
            # Guardar respuesta del asistente
            mensaje_asistente = Mensaje.objects.create(
                conversacion=conversacion,
                rol='assistant',
                contenido=respuesta
            )
            
            # Actualizar fecha de conversación
            conversacion.save()  # Actualiza fecha_actualizacion automáticamente
            
            return Response({
                "conversacion_id": conversacion.id,
                "mensaje_usuario": MensajeSerializer(mensaje_usuario).data,
                "mensaje_asistente": MensajeSerializer(mensaje_asistente).data,
                "respuesta": respuesta
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error al procesar mensaje: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='conversaciones')
    def list_conversaciones(self, request):
        """
        Lista todas las conversaciones del usuario
        GET /api/assistant/conversaciones/
        """
        perfil, empresa = self.get_perfil_and_empresa(request.user)
        if not perfil or not empresa:
            return Response(
                {"error": "Usuario no tiene perfil o empresa asociada"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        conversaciones = Conversacion.objects.filter(
            usuario=request.user,
            empresa=empresa
        )
        
        serializer = ConversacionListSerializer(conversaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='historial')
    def get_historial(self, request, pk=None):
        """
        Obtiene el historial completo de una conversación
        GET /api/assistant/{conversacion_id}/historial/
        """
        perfil, empresa = self.get_perfil_and_empresa(request.user)
        if not perfil or not empresa:
            return Response(
                {"error": "Usuario no tiene perfil o empresa asociada"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            conversacion = Conversacion.objects.get(
                id=pk,
                usuario=request.user,
                empresa=empresa
            )
        except Conversacion.DoesNotExist:
            return Response(
                {"error": "Conversación no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ConversacionSerializer(conversacion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def delete_conversacion(self, request, pk=None):
        """
        Elimina una conversación
        DELETE /api/assistant/{conversacion_id}/
        """
        perfil, empresa = self.get_perfil_and_empresa(request.user)
        if not perfil or not empresa:
            return Response(
                {"error": "Usuario no tiene perfil o empresa asociada"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            conversacion = Conversacion.objects.get(
                id=pk,
                usuario=request.user,
                empresa=empresa
            )
            conversacion.delete()
            return Response(
                {"message": "Conversación eliminada exitosamente"},
                status=status.HTTP_200_OK
            )
        except Conversacion.DoesNotExist:
            return Response(
                {"error": "Conversación no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, pk=None):
        """
        Endpoint estándar para DELETE /api/assistant/{id}/
        """
        return self.delete_conversacion(request, pk)
