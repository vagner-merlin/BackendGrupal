from .serializers import ClienteSerializer, DomicilioSerializer, TrabajoSerializer, DocumentacionSerializer
from .models import Cliente, Domicilio, Trabajo, Documentacion
from app_User.models import Perfiluser
from rest_framework import viewsets, permissions, status 
from rest_framework.response import Response


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Cliente.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Cliente.objects.none()

    def perform_create(self, serializer):
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            pass


class DocumentacionViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Documentacion.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Documentacion.objects.none()

    def perform_create(self, serializer):
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            pass


class TrabajoViewSet(viewsets.ModelViewSet):
    serializer_class = TrabajoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Trabajo.objects.filter(empresa_rel=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Trabajo.objects.none()

    def perform_create(self, serializer):
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa_rel=perfil.empresa)
        except Perfiluser.DoesNotExist:
            pass


class DomicilioViewSet(viewsets.ModelViewSet):
    serializer_class = DomicilioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Domicilio.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Domicilio.objects.none()

    def perform_create(self, serializer):
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            pass
