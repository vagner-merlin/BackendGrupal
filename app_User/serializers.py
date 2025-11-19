from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User  , Group , Permission 
from django.contrib.contenttypes.models import ContentType
from .models import Perfiluser

class UserSerializers(ModelSerializer): 
    password = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada correctamente"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)  # ← Hashea la contraseña
            user.save()
        
        return user
    def update(self, instance, validated_data):
        """Actualizar usuario manteniendo contraseña hasheada"""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)  # ← Hashea la contraseña
        
        instance.save()
        return instance
class GroupSerializers(ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(source='name', required=False, allow_blank=True, max_length=150)
    permisos = serializers.PrimaryKeyRelatedField(
        source='permissions',
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )
    descripcion = serializers.SerializerMethodField()
    empresa_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Group
        fields = ['id', 'nombre', 'permisos', 'descripcion', 'empresa_id']
    
    def to_representation(self, instance):
        """Personalizar la representación para incluir descripción y mapear name -> nombre"""
        data = super().to_representation(instance)
        # Asegurar que el nombre del grupo se devuelve en 'nombre'
        if 'nombre' not in data or not data['nombre']:
            data['nombre'] = instance.name
        # Obtener descripción del modelo relacionado
        try:
            desc = instance.descripcion_obj.descripcion
            data['descripcion'] = desc
        except:
            data['descripcion'] = None
        return data
    
    def get_descripcion(self, obj):
        """Obtener descripción del grupo"""
        try:
            return obj.descripcion_obj.descripcion
        except:
            return None
        
    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', [])
        descripcion = self.initial_data.get('descripcion', '')
        empresa_id = self.initial_data.get('empresa_id', None)
        # Soportar tanto 'nombre' como 'name' en el input
        name = self.initial_data.get('nombre', '') or self.initial_data.get('name', '')
        name = name.strip() if name else ''
        
        # Si name viene vacío o no viene, generar uno de la descripción
        if not name:
            name = descripcion[:150].strip() if descripcion else f'Grupo {Group.objects.count() + 1}'
        
        # Crear el grupo con el nombre
        group = Group.objects.create(name=name)
        
        # Asignar permisos
        if permissions_data:
            group.permissions.set(permissions_data)
        
        # Crear descripción del grupo con empresa
        from app_User.models import GroupDescripcion
        from app_Empresa.models import Empresa
        try:
            empresa = None
            if empresa_id:
                empresa = Empresa.objects.get(id=empresa_id)
            GroupDescripcion.objects.create(group=group, descripcion=descripcion, empresa=empresa)
        except Exception as e:
            print(f"Error creando GroupDescripcion: {e}")
        
        return group
    
    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', None)
        # Soportar tanto 'name' (from source='name') como 'nombre'
        name = validated_data.get('name', '').strip() if validated_data.get('name') else ''
        
        # Actualizar nombre si viene
        if name:
            instance.name = name
        
        instance.save()
        
        # Actualizar permisos
        if permissions_data is not None:
            instance.permissions.set(permissions_data)
        
        # Actualizar descripción
        descripcion = self.initial_data.get('descripcion', None)
        if descripcion is not None:
            try:
                desc_obj = instance.descripcion_obj
                desc_obj.descripcion = descripcion
                desc_obj.save()
            except:
                from app_User.models import GroupDescripcion
                GroupDescripcion.objects.create(group=instance, descripcion=descripcion)
        
        return instance

class PermissionSerializers(ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializers(ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'


class AdminLogSerializer(serializers.Serializer):
    """Serializer de solo-lectura para mostrar los campos del LogEntry
    en el formato solicitado: usuario, tipo_contenido, objeto, accion (texto), mensaje y action_time.
    """
    id = serializers.IntegerField(read_only=True)
    usuario = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    tipo_contenido = serializers.CharField(source='content_type.model', read_only=True, allow_null=True)
    objeto = serializers.CharField(source='object_repr', read_only=True, allow_null=True)
    accion = serializers.SerializerMethodField()
    mensaje = serializers.CharField(source='change_message', read_only=True, allow_null=True)
    action_time = serializers.DateTimeField(read_only=True)

    def get_accion(self, obj):
        """Mapea action_flag a un nombre legible en español."""
        mapping = {
            1: 'Adición',
            2: 'Cambio',
            3: 'Eliminación',
        }
        return mapping.get(getattr(obj, 'action_flag', None), getattr(obj, 'action_flag', None))
    
class PerfilUserSerializer(ModelSerializer):
    class Meta:
        model = Perfiluser
        fields = '__all__'
