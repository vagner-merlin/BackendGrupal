from rest_framework.serializers import ModelSerializer
from .models import Credito, Tipo_Credito, HistoricoCredito


class CreditoSerializer(ModelSerializer):
    class Meta:
        model = Credito
        fields = '__all__'
        read_only_fields = ('empresa', 'usuario', 'fecha_creacion', 'fecha_actualizacion', 'fase_actual')


class TipoCreditoSerializer(ModelSerializer):
    class Meta:
        model = Tipo_Credito
        fields = '__all__'


class HistoricoreditoSerializer(ModelSerializer):
    """Serializer para el histórico de cambios de fase"""
    class Meta:
        model = HistoricoCredito
        fields = '__all__'
        read_only_fields = ('fecha_cambio',)


class CreditoWorkflowSerializer(ModelSerializer):
    """Serializer para operaciones de workflow - crear crédito inicial"""
    class Meta:
        model = Credito
        fields = ('Monto_Solicitado', 'Numero_Cuotas', 'Monto_Cuota', 'Tasa_Interes', 'Moneda', 'tipo_credito')


class AgregarDocumentacionSerializer(ModelSerializer):
    """Serializer para agregar documentación (FASE 2)"""
    class Meta:
        model = Credito
        fields = []
        
        
class AgregarLaboralSerializer(ModelSerializer):
    """Serializer para agregar información laboral (FASE 3)"""
    class Meta:
        model = Credito
        fields = []


class AgregarDomicilioSerializer(ModelSerializer):
    """Serializer para agregar domicilio (FASE 4)"""
    class Meta:
        model = Credito
        fields = []


class AgregarGaranteSerializer(ModelSerializer):
    """Serializer para agregar garante (FASE 5)"""
    class Meta:
        model = Credito
        fields = []


class RevisarCreditoSerializer(ModelSerializer):
    """Serializer para revisar/aprobar/rechazar crédito (FASE 6)"""
    class Meta:
        model = Credito
        fields = ('razon_rechazo',)
