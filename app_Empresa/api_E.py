from app_Empresa.serializers import EmpresaSerializer, RegisterEmpresaUserSerializer, LoginSerializer, LogoutSerializer, SuscripcionSerializer , OnPremiseSerializer , ConfiguracionSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from app_Empresa.models import Empresa, Suscripcion , on_premise , Configuracion
from app_User.models import Perfiluser
from .s3_utils import upload_empresa_logo, upload_user_avatar
import traceback

class ConfiguracionViewSet(viewsets.ModelViewSet):
    serializer_class = ConfiguracionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar configuraciones por empresa del usuario"""
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Configuracion.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Configuracion.objects.none()
    
    def perform_create(self, serializer):
        """Auto-asignar empresa al crear configuración"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            pass

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]  # Soporte para archivos
    
    def update(self, request, *args, **kwargs):
        """Override update para manejar subida de imágenes a S3"""
        instance = self.get_object()
        
        # Si viene una imagen, subirla a S3
        imagen_empresa_file = request.FILES.get('imagen_empresa', None)
        if imagen_empresa_file:
            print(f"🖼️ [EmpresaViewSet] Subiendo logo: {imagen_empresa_file.name}")
            logo_url = upload_empresa_logo(imagen_empresa_file)
            if logo_url:
                print(f"✅ [EmpresaViewSet] Logo subido: {logo_url}")
                # Actualizar el campo directamente en la instancia
                instance.Imagen_url = logo_url
                instance.save()
                print(f"💾 [EmpresaViewSet] Logo guardado en BD: {logo_url}")
        
        return super().update(request, *args, **kwargs)

class OnPremiseViewSet(viewsets.ModelViewSet):
    queryset = on_premise.objects.all()
    serializer_class = OnPremiseSerializer
    permission_classes = [permissions.IsAuthenticated]


class SuscripcionViewSet(viewsets.ModelViewSet):
    serializer_class = SuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar suscripciones por empresa del usuario"""
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Suscripcion.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Suscripcion.objects.none()
    
    def perform_create(self, serializer):
        """Auto-asignar empresa al crear suscripción"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            pass


class RegisterView(APIView):
    """
    API independiente para registrar empresa, usuario y perfil en una sola petición
    """
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def post(self, request):
        serializer = RegisterEmpresaUserSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                
                response_data = {
                    'message': 'Registro exitoso',
                    'empresa': {
                        'id': result['empresa'].id,
                        'razon_social': result['empresa'].razon_social,
                        'email_contacto': result['empresa'].email_contacto,
                        'nombre_comercial': result['empresa'].nombre_comercial,
                        'fecha_registro': result['empresa'].fecha_registro,
                        'activo': result['empresa'].activo,
                        'imagen_url': result['empresa'].Imagen_url,
                    },
                    'user': {
                        'id': result['user'].id,
                        'username': result['user'].username,
                        'first_name': result['user'].first_name,
                        'last_name': result['user'].last_name,
                        'email': result['user'].email,
                        'date_joined': result['user'].date_joined,
                        'is_superuser': result['user'].is_superuser,
                        'is_staff': result['user'].is_staff,
                        'empresa_id': result['perfil_user'].empresa.id,
                        'empresa_nombre': result['empresa'].razon_social,
                    },
                    'perfil_user': {
                        'id': result['perfil_user'].id,
                        'empresa_id': result['perfil_user'].empresa.id,
                        'usuario_id': result['perfil_user'].usuario.id,
                        'imagen_url': result['perfil_user'].imagen_url,
                    },
                    'token': result['token']
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': f'Error interno del servidor: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    """
    API para login con email y password, devuelve token
    """
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                
                response_data = {
                    'message': 'Login exitoso',
                    'token': result['token'],
                     'user': {
                        'id': result['user_id'],
                        'username': result.get('username', ''),
                        'email': result['email'],
                        'nombre_completo': result.get('nombre_completo', ''),
                        'is_superuser': result['is_superuser'],
                        'is_staff': result['is_staff'],
                        'empresa_id': result['empresa_id'],
                        'empresa_nombre': result['empresa_nombre'],
                    }
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response(
                    {'error': f'Error interno del servidor: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """
    API para logout, elimina el token
    """
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                return Response(
                    {'message': 'Logout exitoso'}, 
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                return Response(
                    {'error': f'Error interno del servidor: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterEmpresaUserAPIView(APIView):
    """
    API dedicada para registrar empresa y usuario con subida de imágenes a S3
    Inspirada en ImageUploadAPIView con soporte completo para multipart/form-data
    
    IMPORTANTE: Este endpoint NO requiere autenticación (es para registro público)
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.AllowAny]  # Público para permitir registros
    authentication_classes = []  # Sin autenticación requerida
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch para capturar errores de parsing y debugging"""
        print(f"🔍 [RegisterEmpresa] Dispatch - Method: {request.method}")
        print(f"🔍 [RegisterEmpresa] Content-Type: {request.content_type}")
        print(f"🔍 [RegisterEmpresa] Headers: {dict(request.headers)}")
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ [RegisterEmpresa] Error en dispatch: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            return Response({
                'success': False,
                'error': f'Error en dispatch: {str(e)}',
                'tipo': type(e).__name__
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        """
        Registrar empresa y usuario con imágenes
        
        Parámetros esperados (multipart/form-data):
        - razon_social: string
        - email_contacto: string
        - nombre_comercial: string
        - imagen_empresa: archivo (opcional)
        - username: string
        - password: string
        - first_name: string
        - last_name: string
        - email: string
        - imagen_perfil: archivo (opcional)
        """
        try:
            # DEBUG: Imprimir lo que llega
            print(f"📥 [RegisterEmpresa] FILES recibidos: {list(request.FILES.keys())}")
            print(f"📥 [RegisterEmpresa] DATA recibido: {dict(request.data)}")
            print(f"📥 [RegisterEmpresa] POST recibido: {dict(request.POST)}")
            
            # Extraer archivos
            imagen_empresa_file = request.FILES.get('imagen_empresa', None)
            imagen_perfil_file = request.FILES.get('imagen_perfil', None)
            
            print(f"🖼️ [RegisterEmpresa] Imagen empresa: {imagen_empresa_file.name if imagen_empresa_file else 'No enviada'}")
            print(f"🖼️ [RegisterEmpresa] Imagen perfil: {imagen_perfil_file.name if imagen_perfil_file else 'No enviada'}")
            
            # Preparar datos para el serializer (sin archivos)
            data = {
                'razon_social': request.data.get('razon_social'),
                'email_contacto': request.data.get('email_contacto'),
                'nombre_comercial': request.data.get('nombre_comercial'),
                'username': request.data.get('username'),
                'password': request.data.get('password'),
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                'email': request.data.get('email'),
            }
            
            # Agregar archivos si existen
            if imagen_empresa_file:
                data['imagen_empresa'] = imagen_empresa_file
            if imagen_perfil_file:
                data['imagen_perfil'] = imagen_perfil_file
            
            # Validar campos requeridos
            campos_requeridos = ['razon_social', 'email_contacto', 'nombre_comercial', 
                               'username', 'password', 'first_name', 'last_name', 'email']
            campos_faltantes = [campo for campo in campos_requeridos if not data.get(campo)]
            
            if campos_faltantes:
                return Response({
                    'success': False,
                    'error': 'Faltan campos requeridos',
                    'campos_faltantes': campos_faltantes,
                    'debug': {
                        'data_recibido': list(data.keys()),
                        'files_recibidos': list(request.FILES.keys())
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"✅ [RegisterEmpresa] Datos validados, procesando con serializer...")
            
            # Usar el serializer
            serializer = RegisterEmpresaUserSerializer(data=data)
            
            if serializer.is_valid():
                try:
                    result = serializer.save()
                    
                    print(f"✅ [RegisterEmpresa] Empresa creada con ID: {result['empresa'].id}")
                    print(f"✅ [RegisterEmpresa] Usuario creado: {result['user'].username}")
                    print(f"🖼️ [RegisterEmpresa] Logo empresa URL: {result['empresa'].Imagen_url}")
                    print(f"🖼️ [RegisterEmpresa] Avatar usuario URL: {result['perfil_user'].imagen_url}")
                    
                    response_data = {
                        'success': True,
                        'message': 'Registro exitoso',
                        'empresa': {
                            'id': result['empresa'].id,
                            'razon_social': result['empresa'].razon_social,
                            'email_contacto': result['empresa'].email_contacto,
                            'nombre_comercial': result['empresa'].nombre_comercial,
                            'fecha_registro': result['empresa'].fecha_registro,
                            'activo': result['empresa'].activo,
                            'imagen_url': result['empresa'].Imagen_url,
                        },
                        'user': {
                            'id': result['user'].id,
                            'username': result['user'].username,
                            'first_name': result['user'].first_name,
                            'last_name': result['user'].last_name,
                            'email': result['user'].email,
                            'date_joined': result['user'].date_joined,
                            'is_superuser': result['user'].is_superuser,
                            'is_staff': result['user'].is_staff,
                            'empresa_id': result['perfil_user'].empresa.id,
                            'empresa_nombre': result['empresa'].razon_social,
                        },
                        'perfil_user': {
                            'id': result['perfil_user'].id,
                            'empresa_id': result['perfil_user'].empresa.id,
                            'usuario_id': result['perfil_user'].usuario.id,
                            'imagen_url': result['perfil_user'].imagen_url,
                        },
                        'token': result['token']
                    }
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    print(f"❌ [RegisterEmpresa] Error al guardar: {str(e)}")
                    traceback.print_exc()
                    return Response(
                        {
                            'success': False,
                            'error': f'Error interno del servidor: {str(e)}',
                            'tipo_error': type(e).__name__
                        }, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                print(f"❌ [RegisterEmpresa] Errores de validación: {serializer.errors}")
                return Response(
                    {
                        'success': False,
                        'errors': serializer.errors
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            print(f"❌ [RegisterEmpresa] Error general: {str(e)}")
            traceback.print_exc()
            return Response({
                'success': False,
                'error': f'Error al procesar registro: {str(e)}',
                'tipo_error': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request, *args, **kwargs):
        """
        Obtener información sobre la configuración de S3 y el endpoint
        """
        from django.conf import settings
        
        return Response({
            'endpoint': '/api/empresa/register/empresa-user/',
            'method': 'POST',
            'content_type': 'multipart/form-data',
            'campos_requeridos': [
                'razon_social',
                'email_contacto',
                'nombre_comercial',
                'username',
                'password',
                'first_name',
                'last_name',
                'email'
            ],
            'campos_opcionales': [
                'imagen_empresa (archivo)',
                'imagen_perfil (archivo)'
            ],
            's3_config': {
                'bucket_name': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'No configurado'),
                's3_region': getattr(settings, 'AWS_S3_REGION_NAME', 'No configurado'),
            }
        })


