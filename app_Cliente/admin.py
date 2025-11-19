from django.contrib import admin
from .models import Trabajo, Documentacion, Garante, Cliente, Domicilio

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'telefono', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('nombre', 'apellido', 'telefono')
    readonly_fields = ('fecha_registro',)
    date_hierarchy = 'fecha_registro'
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'telefono')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Trabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cargo', 'empresa', 'salario', 'ubicacion')
    list_filter = ('empresa', 'ubicacion')
    search_fields = ('cargo', 'empresa', 'ubicacion')
    
    fieldsets = (
        ('Información Laboral', {
            'fields': ('cargo', 'empresa', 'ubicacion', 'salario')
        }),
        ('Documentos', {
            'fields': ('extracto_url',)
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
    )

@admin.register(Documentacion)
class DocumentacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ci', 'documento_url', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('ci',)
    readonly_fields = ('fecha_registro',)
    date_hierarchy = 'fecha_registro'
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Identificación', {
            'fields': ('ci',)
        }),
        ('Documento', {
            'fields': ('documento_url',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Garante)
class GaranteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombrecompleto', 'ci', 'telefono')
    search_fields = ('nombrecompleto', 'ci', 'telefono')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombrecompleto', 'ci', 'telefono')
        }),
    )

@admin.register(Domicilio)
class DomicilioAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'es_propietario', 'numero_ref')
    list_filter = ('es_propietario',)
    search_fields = ('descripcion', 'numero_ref')
    
    fieldsets = (
        ('Información de Domicilio', {
            'fields': ('descripcion', 'es_propietario', 'numero_ref')
        }),
        ('Documentos', {
            'fields': ('croquis_url',)
        }),
    )
