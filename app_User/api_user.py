from django.contrib.auth.models import User , Group , Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from .serializers import (
    UserSerializers , GroupSerializers , PermissionSerializers , ContentTypeSerializers,
    AdminLogSerializer, PerfilUserSerializer
)
from rest_framework import viewsets , permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from app_User.models import Perfiluser
from app_Empresa.models import Empresa
from .models import Perfiluser


# drf-spectacular is optional; if not installed, provide a no-op decorator.
try:
    from drf_spectacular.utils import extend_schema
except Exception:
    def extend_schema(*args, **kwargs):
        def _decorator(obj):
            return obj
        return _decorator


class UserViewSer(viewsets.ModelViewSet):
    serializer_class = UserSerializers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar usuarios por empresa del usuario autenticado (multitenancy)"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            # Retornar solo los usuarios de la empresa del usuario
            return User.objects.filter(
                perfiluser__empresa=perfil.empresa
            ).order_by("id")
        except Perfiluser.DoesNotExist:
            # Si no tiene perfil, retornar vacío
            return User.objects.none()

    def perform_create(self, serializer):
        """Auto-asignar la empresa al crear usuario"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            raise ValidationError("Usuario no tiene perfil asociado")


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar grupos por empresa del usuario autenticado (multitenancy)"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            # Retornar solo los grupos de la empresa del usuario
            return Group.objects.filter(
                descripcion_obj__empresa=perfil.empresa
            ).order_by("id")
        except Perfiluser.DoesNotExist:
            # Si no tiene perfil, retornar vacío
            return Group.objects.none()

    def create(self, request, *args, **kwargs):
        """Crear grupo asociado a la empresa del usuario autenticado"""
        try:
            # Verificar que el usuario tiene perfil
            perfil = Perfiluser.objects.get(usuario=request.user)
            
            # Agregar la empresa al request data
            request.data['empresa_id'] = perfil.empresa.id
            
            return super().create(request, *args, **kwargs)
        except Perfiluser.DoesNotExist:
            return Response({"error": "Usuario no tiene perfil asociado"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PermissionViewSer(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializers
    permission_classes = [permissions.IsAuthenticated]

class ContentTypeViewSer(viewsets.ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializers
    permission_classes = [permissions.IsAuthenticated]


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API read-only que expone las entradas del log de administrador en el formato solicitado.

    GET /api/User/admin-log/  -> lista paginada por defecto (si DRF lo aplica)
    """
    queryset = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
    serializer_class = AdminLogSerializer
    permission_classes = [permissions.AllowAny]


class CreateUserView(APIView):
    """
    API para crear usuarios normales dentro de la misma empresa del administrador autenticado.
    Solo un administrador (is_staff=True) puede crear usuarios para su propia empresa.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def post(self, request):
        # Solo administradores pueden crear usuarios normales
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        # Obtener empresa del admin (perfil)
        try:
            admin_perfil = Perfiluser.objects.get(usuario=request.user)
        except Perfiluser.DoesNotExist:
            return Response({'error': 'Administrador no tiene perfil asociado'}, status=status.HTTP_403_FORBIDDEN)

        # Obtener datos del request
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        # Forzamos que la empresa sea la del admin, o puede recibirse para validación
        empresa_id = request.data.get('empresa_id', admin_perfil.empresa.id)
        imagen_url = request.data.get('imagen_url', '')

        # Validaciones básicas
        if not all([username, password, email]):
            return Response({'error': 'username, password y email son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que la empresa solicitada coincide con la del admin
        if int(empresa_id) != admin_perfil.empresa.id:
            return Response({'error': 'Solo puede crear usuarios para su propia empresa'}, status=status.HTTP_403_FORBIDDEN)

        # Verificar que el username y email no existan
        if User.objects.filter(username=username).exists():
            return Response({'error': 'El username ya existe'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'El email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Crear usuario normal (no admin)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )

            # Crear perfil de usuario vinculado a la misma empresa del admin
            perfil_user = Perfiluser.objects.create(empresa=admin_perfil.empresa, usuario=user, imagen_url=imagen_url)

            # Crear token
            token, created = Token.objects.get_or_create(user=user)

            response_data = {
                'message': 'Usuario creado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'empresa_id': admin_perfil.empresa.id,
                    'empresa_nombre': admin_perfil.empresa.razon_social,
                },
                'token': token.key
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Error al crear usuario: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PerfilUserViewSet(viewsets.ModelViewSet):
    queryset = Perfiluser.objects.all()
    serializer_class = PerfilUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def update(self, request, *args, **kwargs):
        """Override update para manejar subida de avatar a S3"""
        from app_Empresa.s3_utils import upload_user_avatar
        
        instance = self.get_object()
        
        # Si viene una imagen de perfil, subirla a S3
        imagen_perfil_file = request.FILES.get('imagen_perfil', None) or request.FILES.get('imagen_url', None)
        if imagen_perfil_file:
            print(f"🖼️ [PerfilUserViewSet] Subiendo avatar: {imagen_perfil_file.name}")
            avatar_url = upload_user_avatar(imagen_perfil_file)
            if avatar_url:
                print(f"✅ [PerfilUserViewSet] Avatar subido: {avatar_url}")
                # Actualizar el campo directamente en la instancia
                instance.imagen_url = avatar_url
                instance.save()
                print(f"💾 [PerfilUserViewSet] Avatar guardado en BD: {avatar_url}")
        
        return super().update(request, *args, **kwargs)