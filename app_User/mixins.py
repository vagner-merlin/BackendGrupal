"""
Mixin para multitenancy: Filtra automáticamente todos los querysets por empresa del usuario
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from app_User.models import Perfiluser


class TenantFilterMixin:
    """
    Mixin que filtra TODOS los querysets por la empresa del usuario autenticado.
    Uso: class MiViewSet(TenantFilterMixin, viewsets.ModelViewSet):
    """
    
    def get_queryset(self):
        """Filtrar queryset por empresa del usuario autenticado"""
        queryset = super().get_queryset()
        
        # Si no hay usuario autenticado, retornar vacío
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            # Filtrar por empresa del usuario
            return queryset.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            # Si no tiene perfil, retornar vacío
            return queryset.none()
    
    def get_tenant_empresa(self):
        """Obtener la empresa del usuario actual"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            return perfil.empresa
        except Perfiluser.DoesNotExist:
            return None
    
    def perform_create(self, serializer):
        """Auto-asignar empresa al crear objetos"""
        empresa = self.get_tenant_empresa()
        if empresa:
            serializer.save(empresa=empresa)
        else:
            raise PermissionError("Usuario no tiene empresa asociada")
    
    def perform_update(self, serializer):
        """Validar que se actualice solo dentro de la misma empresa"""
        empresa = self.get_tenant_empresa()
        if serializer.instance.empresa != empresa:
            raise PermissionError("No puedes actualizar datos de otra empresa")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Validar que se elimine solo dentro de la misma empresa"""
        empresa = self.get_tenant_empresa()
        if instance.empresa != empresa:
            raise PermissionError("No puedes eliminar datos de otra empresa")
        instance.delete()
