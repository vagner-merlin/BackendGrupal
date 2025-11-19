from .models import Credito, Tipo_Credito, HistoricoCredito
from .serializers import (
    CreditoSerializer, TipoCreditoSerializer, HistoricoreditoSerializer,
    CreditoWorkflowSerializer, AgregarDocumentacionSerializer
)
from .workflow import cambiar_fase, validar_fase_secuencial, obtener_linea_tiempo, obtener_estado_actual
from app_User.models import Perfiluser
from app_Cliente.models import Documentacion, Trabajo, Domicilio, Garante
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import datetime


class TipoCreditoViewSet(viewsets.ModelViewSet):
    serializer_class = TipoCreditoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar tipos de crédito por empresa del usuario"""
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Tipo_Credito.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Tipo_Credito.objects.none()
    
    def perform_create(self, serializer):
        """Auto-asignar empresa al crear tipo de crédito"""
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            raise ValidationError("No se encontró el perfil de usuario. Contacta al administrador.")


class CreditoViewSet(viewsets.ModelViewSet):
    serializer_class = CreditoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            perfil = Perfiluser.objects.get(usuario=user)
            return Credito.objects.filter(empresa=perfil.empresa)
        except Perfiluser.DoesNotExist:
            return Credito.objects.none()

    def perform_create(self, serializer):
        try:
            perfil = Perfiluser.objects.get(usuario=self.request.user)
            serializer.save(empresa=perfil.empresa, usuario=self.request.user)
        except Perfiluser.DoesNotExist:
            pass

    @action(detail=True, methods=['get'], url_path='linea-tiempo')
    def linea_tiempo(self, request, pk=None):
        """Obtiene la línea de tiempo completa del crédito"""
        try:
            credito = self.get_object()
            linea = obtener_linea_tiempo(credito)
            return Response({
                'credito_id': credito.id,
                'linea_tiempo': linea,
                'total_cambios': len(linea),
            })
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='estado-actual')
    def estado_actual(self, request, pk=None):
        """Obtiene el estado actual del crédito con información detallada"""
        try:
            credito = self.get_object()
            estado = obtener_estado_actual(credito)
            return Response(estado)
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], url_path='agregar-documentacion')
    def agregar_documentacion(self, request, pk=None):
        """Agrega documentación y avanza a FASE_2"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_1
            if credito.fase_actual != 'FASE_1_SOLICITUD':
                raise ValidationError(f"Debe estar en FASE_1_SOLICITUD, actualmente está en {credito.fase_actual}")
            
            # Extraer datos
            ci = request.data.get('ci')
            documento_url = request.data.get('documento_url')
            
            if not all([ci, documento_url]):
                raise ValidationError("ci y documento_url son requeridos")
            
            # Crear o actualizar documentación
            doc, created = Documentacion.objects.update_or_create(
                id_cliente=credito.cliente,
                defaults={
                    'ci': ci,
                    'documento_url': documento_url,
                    'empresa': credito.empresa,
                }
            )
            
            # Cambiar fase
            cambiar_fase(
                credito=credito,
                fase_nueva='FASE_2_DOCUMENTACION',
                usuario=request.user,
                descripcion='Documentación personal agregada',
                datos_agregados={'ci': ci, 'documento_url': documento_url}
            )
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': 'Documentación agregada exitosamente',
                'fase_nueva': credito.fase_actual,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='agregar-laboral')
    def agregar_laboral(self, request, pk=None):
        """Agrega información laboral y avanza a FASE_3"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_2
            if credito.fase_actual != 'FASE_2_DOCUMENTACION':
                raise ValidationError(f"Debe completar FASE_2 primero, actualmente está en {credito.fase_actual}")
            
            # Extraer datos
            cargo = request.data.get('cargo')
            empresa = request.data.get('empresa')
            salario = request.data.get('salario')
            extracto_url = request.data.get('extracto_url')
            
            if not all([cargo, empresa, salario, extracto_url]):
                raise ValidationError("cargo, empresa, salario y extracto_url son requeridos")
            
            # Crear o actualizar trabajo
            trabajo, created = Trabajo.objects.update_or_create(
                id_cliente=credito.cliente,
                defaults={
                    'cargo': cargo,
                    'empresa': empresa,
                    'salario': salario,
                    'extracto_url': extracto_url,
                    'empresa_rel': credito.empresa,
                }
            )
            
            # Cambiar fase
            cambiar_fase(
                credito=credito,
                fase_nueva='FASE_3_LABORAL',
                usuario=request.user,
                descripcion='Información laboral agregada',
                datos_agregados={'cargo': cargo, 'empresa': empresa, 'salario': str(salario)}
            )
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': 'Información laboral agregada exitosamente',
                'fase_nueva': credito.fase_actual,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='agregar-domicilio')
    def agregar_domicilio(self, request, pk=None):
        """Agrega domicilio y avanza a FASE_4"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_3
            if credito.fase_actual != 'FASE_3_LABORAL':
                raise ValidationError(f"Debe completar FASE_3 primero, actualmente está en {credito.fase_actual}")
            
            # Extraer datos
            descripcion = request.data.get('descripcion')
            croquis_url = request.data.get('croquis_url')
            es_propietario = request.data.get('es_propietario')
            numero_ref = request.data.get('numero_ref')
            
            if not all([descripcion, croquis_url, numero_ref]):
                raise ValidationError("descripcion, croquis_url y numero_ref son requeridos")
            
            # Crear o actualizar domicilio
            domicilio, created = Domicilio.objects.update_or_create(
                id_cliente=credito.cliente,
                defaults={
                    'descripcion': descripcion,
                    'croquis_url': croquis_url,
                    'es_propietario': es_propietario,
                    'numero_ref': numero_ref,
                    'empresa': credito.empresa,
                }
            )
            
            # Cambiar fase
            cambiar_fase(
                credito=credito,
                fase_nueva='FASE_4_DOMICILIO',
                usuario=request.user,
                descripcion='Domicilio agregado',
                datos_agregados={'descripcion': descripcion, 'es_propietario': es_propietario}
            )
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': 'Domicilio agregado exitosamente',
                'fase_nueva': credito.fase_actual,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='agregar-garante')
    def agregar_garante(self, request, pk=None):
        """Agrega datos del garante y avanza a FASE_5"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_4
            if credito.fase_actual != 'FASE_4_DOMICILIO':
                raise ValidationError(f"Debe completar FASE_4 primero, actualmente está en {credito.fase_actual}")
            
            # Obtener domicilio del cliente
            try:
                domicilio = Domicilio.objects.get(id_cliente=credito.cliente)
            except Domicilio.DoesNotExist:
                raise ValidationError("Debe completar domicilio antes de agregar garante")
            
            # Extraer datos
            nombrecompleto = request.data.get('nombrecompleto')
            ci = request.data.get('ci')
            telefono = request.data.get('telefono')
            
            if not all([nombrecompleto, ci, telefono]):
                raise ValidationError("nombrecompleto, ci y telefono son requeridos")
            
            # Crear o actualizar garante
            garante, created = Garante.objects.update_or_create(
                id_domicilio=domicilio,
                defaults={
                    'nombrecompleto': nombrecompleto,
                    'ci': ci,
                    'telefono': telefono,
                    'empresa': credito.empresa,
                }
            )
            
            # Cambiar fase
            cambiar_fase(
                credito=credito,
                fase_nueva='FASE_5_GARANTE',
                usuario=request.user,
                descripcion='Datos del garante agregados',
                datos_agregados={'nombrecompleto': nombrecompleto, 'ci': ci, 'telefono': telefono}
            )
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': 'Datos del garante agregados exitosamente',
                'fase_nueva': credito.fase_actual,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='enviar-revision')
    def enviar_revision(self, request, pk=None):
        """Envía el crédito a revisión (FASE_6)"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_5
            if credito.fase_actual != 'FASE_5_GARANTE':
                raise ValidationError(f"Debe completar todas las fases primero, actualmente está en {credito.fase_actual}")
            
            # Cambiar fase a revisión
            cambiar_fase(
                credito=credito,
                fase_nueva='FASE_6_REVISION',
                usuario=request.user,
                descripcion='Solicitud de crédito enviada a revisión'
            )
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': 'Solicitud enviada a revisión exitosamente',
                'fase_nueva': credito.fase_actual,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='revisar')
    def revisar_credito(self, request, pk=None):
        """Analista aprueba o rechaza el crédito (FASE_6)"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_6
            if credito.fase_actual != 'FASE_6_REVISION':
                raise ValidationError(f"Solo se puede revisar créditos en FASE_6_REVISION")
            
            aprobado = request.data.get('aprobado')
            razon = request.data.get('razon', '')
            
            if aprobado is None:
                raise ValidationError("Campo 'aprobado' es requerido (true/false)")
            
            if aprobado:
                # Aprobar: cambiar estado y avanzar a FASE_7
                credito.enum_estado = 'Aprobado'
                credito.Fecha_Aprobacion = timezone.now().date()
                
                cambiar_fase(
                    credito=credito,
                    fase_nueva='FASE_7_DESEMBOLSO',
                    usuario=request.user,
                    descripcion='Crédito aprobado'
                )
                
                mensaje = 'Crédito aprobado exitosamente'
            else:
                # Rechazar: cambiar estado a Rechazado y mantener en FASE_6
                credito.enum_estado = 'Rechazado'
                credito.razon_rechazo = razon
                credito.save()
                
                cambiar_fase(
                    credito=credito,
                    fase_nueva='FASE_6_REVISION',
                    usuario=request.user,
                    descripcion=f'Crédito rechazado: {razon}'
                )
                
                mensaje = 'Crédito rechazado'
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': mensaje,
                'estado_actual': credito.enum_estado,
                'fase_nueva': credito.fase_actual,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='desembolsar')
    def desembolsar(self, request, pk=None):
        """Realiza el desembolso del crédito (FASE_7)"""
        try:
            credito = self.get_object()
            
            # Validar que está en FASE_7 y fue aprobado
            if credito.fase_actual != 'FASE_7_DESEMBOLSO':
                raise ValidationError(f"Solo se puede desembolsar en FASE_7_DESEMBOLSO")
            
            if credito.enum_estado != 'Aprobado':
                raise ValidationError("El crédito debe estar aprobado para desembolsar")
            
            # Actualizar datos de desembolso
            credito.enum_estado = 'DESENBOLSADO'
            credito.Fecha_Desembolso = timezone.now().date()
            
            cambiar_fase(
                credito=credito,
                fase_nueva='FASE_8_FINALIZADO',
                usuario=request.user,
                descripcion='Crédito desembolsado exitosamente'
            )
            
            estado = obtener_estado_actual(credito)
            return Response({
                'mensaje': 'Crédito desembolsado exitosamente',
                'estado_actual': credito.enum_estado,
                'fecha_desembolso': credito.Fecha_Desembolso,
                'estado': estado,
            }, status=status.HTTP_200_OK)
            
        except Credito.DoesNotExist:
            return Response({'error': 'Crédito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
