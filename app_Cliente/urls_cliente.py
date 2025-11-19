from django.urls import path , include  
from . import views
from rest_framework import routers
from .api_cliente import ClienteViewSet, DocumentacionViewSet , DomicilioViewSet ,TrabajoViewSet 

router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'documentacion', DocumentacionViewSet, basename='documentacion')
router.register(r'domicilios', DomicilioViewSet, basename='domicilio')
router.register(r'trabajo', TrabajoViewSet, basename='trabajo')

urlpatterns = [
    path('', include(router.urls)),
] 
