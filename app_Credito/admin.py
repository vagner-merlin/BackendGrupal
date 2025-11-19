from django.contrib import admin
from .models import Tipo_Credito, Credito, Ganancia_Credito

@admin.register(Tipo_Credito)
class TipoCreditoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'empresa', 'monto_minimo', 'monto_maximo')
    list_filter = ('empresa',)
    search_fields = ('nombre', 'descripcion')
    autocomplete_fields = ('empresa',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'empresa')
        }),
        ('Límites de Monto', {
            'fields': ('monto_minimo', 'monto_maximo')
        }),
    )

@admin.register(Credito)
class CreditoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'empresa_nombre', 'Monto_Solicitado', 'enum_estado', 'Moneda')
    list_filter = ('enum_estado', 'Moneda', 'empresa')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'empresa__razon_social', 'usuario__username')
    autocomplete_fields = ('empresa', 'usuario', 'cliente', 'tipo_credito')
    ordering = ('-Fecha_Aprobacion',)
    
    def cliente_nombre(self, obj):
        return f"{obj.cliente.nombre} {obj.cliente.apellido}"
    cliente_nombre.short_description = 'Cliente'
    
    def empresa_nombre(self, obj):
        return obj.empresa.razon_social
    empresa_nombre.short_description = 'Empresa'
    
    fieldsets = (
        ('Relaciones', {
            'fields': ('empresa', 'usuario', 'cliente', 'tipo_credito')
        }),
        ('Detalles del Crédito', {
            'fields': ('Monto_Solicitado', 'Monto_Pagar', 'Numero_Cuotas', 'Monto_Cuota', 'Moneda', 'Tasa_Interes')
        }),
        ('Estado y Fechas', {
            'fields': ('enum_estado', 'Fecha_Aprobacion', 'Fecha_Desembolso', 'Fecha_Finalizacion')
        }),
    )

@admin.register(Ganancia_Credito)
class GananciaCreditoAdmin(admin.ModelAdmin):
    list_display = ('id', 'credito_id', 'cliente_nombre', 'monto_prestado', 'tasa_interes', 'duracion_meses')
    list_filter = ('tasa_interes', 'duracion_meses')
    search_fields = ('Cliente__nombre', 'Cliente__apellido', 'Credito__id')
    
    def credito_id(self, obj):
        return f"Crédito #{obj.Credito.id}"
    credito_id.short_description = 'Crédito'
    
    def cliente_nombre(self, obj):
        return f"{obj.Cliente.nombre} {obj.Cliente.apellido}"
    cliente_nombre.short_description = 'Cliente'
    
    fieldsets = (
        ('Relaciones', {
            'fields': ('Credito', 'Cliente')
        }),
        ('Detalles Financieros', {
            'fields': ('monto_prestado', 'tasa_interes', 'duracion_meses', 'ganacia_esperada')
        }),
    )
