from django.contrib import admin
from .models import Empresa, Configuracion, Suscripcion, PagoSuscripcion, on_premise

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'razon_social', 'nombre_comercial', 'email_contacto', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('razon_social', 'nombre_comercial', 'email_contacto')
    readonly_fields = ('fecha_registro',)
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'nombre_comercial', 'email_contacto')
        }),
        ('Estado y Configuración', {
            'fields': ('activo', 'Imagen_url')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'enum_tema', 'color', 'tipo_letra')
    list_filter = ('enum_tema',)
    search_fields = ('empresa__razon_social', 'empresa__nombre_comercial')
    autocomplete_fields = ('empresa',)
    
    fieldsets = (
        ('Empresa', {
            'fields': ('empresa',)
        }),
        ('Configuración Visual', {
            'fields': ('color', 'tipo_letra', 'enum_tema')
        }),
    )

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'enum_plan', 'enum_estado', 'activo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('enum_plan', 'enum_estado', 'activo', 'fecha_inicio')
    search_fields = ('empresa__razon_social', 'empresa__nombre_comercial')
    readonly_fields = ('fecha_inicio',)
    autocomplete_fields = ('empresa',)
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)
    
    fieldsets = (
        ('Empresa', {
            'fields': ('empresa',)
        }),
        ('Detalles de Suscripción', {
            'fields': ('enum_plan', 'enum_estado', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
    )

@admin.register(PagoSuscripcion)
class PagoSuscripcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'suscripcion', 'monto_pagado', 'fecha_pago', 'fecha_proximo_pago')
    list_filter = ('fecha_pago', 'fecha_proximo_pago')
    search_fields = ('suscripcion__empresa__razon_social',)
    readonly_fields = ('fecha_pago',)
    autocomplete_fields = ('suscripcion',)
    date_hierarchy = 'fecha_pago'
    ordering = ('-fecha_pago',)
    
    fieldsets = (
        ('Suscripción', {
            'fields': ('suscripcion',)
        }),
        ('Detalles del Pago', {
            'fields': ('monto_pagado', 'fecha_proximo_pago')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_pago',),
            'classes': ('collapse',)
        }),
    )

@admin.register(on_premise)
class OnPremiseAdmin(admin.ModelAdmin):
    list_display = ('id', 'razon_social', 'email_contacto', 'version', 'fecha_instalacion', 'fecha_sin_soporte')
    list_filter = ('fecha_instalacion', 'fecha_de_compra', 'fecha_sin_soporte')
    search_fields = ('razon_social', 'email_contacto', 'version')
    readonly_fields = ('fecha_instalacion',)
    date_hierarchy = 'fecha_instalacion'
    ordering = ('-fecha_instalacion',)
    
    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('razon_social', 'email_contacto')
        }),
        ('Detalles del Software', {
            'fields': ('version',)
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_de_compra', 'fecha_sin_soporte', 'fecha_instalacion')
        }),
    )
