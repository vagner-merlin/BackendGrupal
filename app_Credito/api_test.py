"""
Endpoint de prueba para verificar que la API de tipos de crédito funciona
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Tipo_Credito
from app_User.models import Perfiluser

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def test_tipo_credito(request):
    """
    GET: Ver tipos de crédito disponibles para la empresa del usuario
    POST: Crear un tipo de crédito (requiere admin)
    """
    user = request.user
    
    try:
        perfil = Perfiluser.objects.get(usuario=user)
        empresa = perfil.empresa
    except Perfiluser.DoesNotExist:
        return Response(
            {'error': 'No se encontró el perfil del usuario'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'GET':
        tipos = Tipo_Credito.objects.filter(empresa=empresa)
        return Response({
            'success': True,
            'empresa': empresa.razon_social if empresa else 'Sin empresa',
            'tipos_credito': [
                {
                    'id': t.id,
                    'nombre': t.nombre,
                    'descripcion': t.descripcion,
                    'monto_minimo': float(t.monto_minimo),
                    'monto_maximo': float(t.monto_maximo),
                }
                for t in tipos
            ],
            'total': tipos.count()
        })
    
    if request.method == 'POST':
        if not user.is_staff:
            return Response(
                {'error': 'Solo administradores pueden crear tipos de crédito'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        try:
            tipo = Tipo_Credito.objects.create(
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion', ''),
                monto_minimo=data.get('monto_minimo'),
                monto_maximo=data.get('monto_maximo'),
                empresa=empresa
            )
            return Response({
                'success': True,
                'message': 'Tipo de crédito creado exitosamente',
                'tipo': {
                    'id': tipo.id,
                    'nombre': tipo.nombre,
                    'descripcion': tipo.descripcion,
                    'monto_minimo': float(tipo.monto_minimo),
                    'monto_maximo': float(tipo.monto_maximo),
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Error creando tipo de crédito: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
