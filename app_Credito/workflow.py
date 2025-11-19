"""
Servicios y funciones para manejar el workflow de créditos
"""
from django.utils import timezone
from .models import Credito, HistoricoCredito, ENUM_FASE_CREDITO
from app_Cliente.models import Documentacion, Trabajo, Domicilio, Garante
from rest_framework.exceptions import ValidationError


def cambiar_fase(credito, fase_nueva, usuario, descripcion="", datos_agregados=None):
    """
    Cambia el crédito a una nueva fase y registra en el histórico
    
    Args:
        credito: Objeto Credito
        fase_nueva: Nueva fase (debe ser una opción válida en ENUM_FASE_CREDITO)
        usuario: Usuario que realiza el cambio
        descripcion: Descripción del cambio
        datos_agregados: Dict con datos agregados en esta fase
    
    Returns:
        HistoricoCredito creado
    """
    if datos_agregados is None:
        datos_agregados = {}
    
    # Crear registro en histórico
    historico = HistoricoCredito.objects.create(
        credito=credito,
        fase_anterior=credito.fase_actual,
        fase_nueva=fase_nueva,
        usuario_cambio=usuario,
        descripcion=descripcion,
        datos_agregados=datos_agregados
    )
    
    # Actualizar la fase actual del crédito
    credito.fase_actual = fase_nueva
    credito.save()
    
    return historico


def validar_fase_secuencial(fase_actual, fase_solicitada):
    """
    Valida que la fase solicitada sea la siguiente en la secuencia
    
    Args:
        fase_actual: Fase actual del crédito
        fase_solicitada: Fase que se quiere alcanzar
    
    Raises:
        ValidationError si no es válido
    """
    secuencia_fases = [
        'FASE_1_SOLICITUD',
        'FASE_2_DOCUMENTACION',
        'FASE_3_LABORAL',
        'FASE_4_DOMICILIO',
        'FASE_5_GARANTE',
        'FASE_6_REVISION',
        'FASE_7_DESEMBOLSO',
        'FASE_8_FINALIZADO',
    ]
    
    idx_actual = secuencia_fases.index(fase_actual)
    idx_solicitada = secuencia_fases.index(fase_solicitada)
    
    # Solo permite avanzar a la siguiente fase o más adelante
    if idx_solicitada <= idx_actual:
        raise ValidationError(
            f"No puede retroceder de fase. Actualmente está en {fase_actual}"
        )
    
    if idx_solicitada > idx_actual + 1:
        raise ValidationError(
            f"Debe completar las fases intermedias. Próxima fase: {secuencia_fases[idx_actual + 1]}"
        )


def obtener_linea_tiempo(credito):
    """
    Obtiene la línea de tiempo completa de un crédito
    
    Args:
        credito: Objeto Credito
    
    Returns:
        Lista de dict con el histórico formateado
    """
    historico = HistoricoCredito.objects.filter(credito=credito)
    
    linea_tiempo = []
    for evento in historico:
        linea_tiempo.append({
            'fase_anterior': evento.fase_anterior,
            'fase_nueva': evento.fase_nueva,
            'fecha_cambio': evento.fecha_cambio,
            'usuario': evento.usuario_cambio.username if evento.usuario_cambio else 'Sistema',
            'descripcion': evento.descripcion,
            'datos_agregados': evento.datos_agregados,
        })
    
    return linea_tiempo


def obtener_estado_actual(credito):
    """
    Obtiene el estado actual del crédito con información detallada
    
    Args:
        credito: Objeto Credito
    
    Returns:
        Dict con el estado actual
    """
    # Información del cliente
    cliente_info = {
        'id': credito.cliente.id,
        'nombre': credito.cliente.nombre,
        'apellido': credito.cliente.apellido,
        'telefono': credito.cliente.telefono,
    }
    
    # Información de documentación
    documentacion_info = {}
    try:
        doc = Documentacion.objects.get(id_cliente=credito.cliente)
        documentacion_info = {
            'ci': doc.ci,
            'documento_url': doc.documento_url,
        }
    except Documentacion.DoesNotExist:
        pass
    
    # Información laboral
    laboral_info = {}
    try:
        trabajo = Trabajo.objects.get(id_cliente=credito.cliente)
        laboral_info = {
            'cargo': trabajo.cargo,
            'empresa': trabajo.empresa,
            'salario': str(trabajo.salario),
            'extracto_url': trabajo.extracto_url,
        }
    except Trabajo.DoesNotExist:
        pass
    
    # Información de domicilio
    domicilio_info = {}
    try:
        domicilio = Domicilio.objects.get(id_cliente=credito.cliente)
        domicilio_info = {
            'descripcion': domicilio.descripcion,
            'es_propietario': domicilio.es_propietario,
            'croquis_url': domicilio.croquis_url,
            'numero_ref': domicilio.numero_ref,
        }
    except Domicilio.DoesNotExist:
        pass
    
    # Información de garante
    garante_info = {}
    try:
        if domicilio_info:
            domicilio = Domicilio.objects.get(id_cliente=credito.cliente)
            garante = Garante.objects.get(id_domicilio=domicilio)
            garante_info = {
                'nombrecompleto': garante.nombrecompleto,
                'ci': garante.ci,
                'telefono': garante.telefono,
            }
    except (Domicilio.DoesNotExist, Garante.DoesNotExist):
        pass
    
    return {
        'credito_id': credito.id,
        'fase_actual': credito.fase_actual,
        'estado': credito.enum_estado,
        'cliente': cliente_info,
        'documentacion': documentacion_info,
        'laboral': laboral_info,
        'domicilio': domicilio_info,
        'garante': garante_info,
        'monto_solicitado': str(credito.Monto_Solicitado),
        'moneda': credito.Moneda,
        'fecha_creacion': credito.fecha_creacion,
        'fecha_actualizacion': credito.fecha_actualizacion,
    }
