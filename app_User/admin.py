from django.contrib import admin
from .models import Perfiluser

@admin.register(Perfiluser)
class PerfiluserAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'empresa', 'usuario_email', 'empresa_nombre')
    list_filter = ('empresa__activo',)
    search_fields = ('usuario__username', 'usuario__email', 'usuario__first_name', 'usuario__last_name', 'empresa__razon_social')
    autocomplete_fields = ('usuario', 'empresa')
    
    def usuario_email(self, obj):
        return obj.usuario.email
    usuario_email.short_description = 'Email del Usuario'
    usuario_email.admin_order_field = 'usuario__email'
    
    def empresa_nombre(self, obj):
        return obj.empresa.razon_social
    empresa_nombre.short_description = 'Empresa'
    empresa_nombre.admin_order_field = 'empresa__razon_social'
    
    fieldsets = (
        ('Relaciones', {
            'fields': ('usuario', 'empresa')
        }),
        ('Información Adicional', {
            'fields': ('imagen_url',)
        }),
    )
