from django.urls import path , include
from rest_framework import routers
from app_Empresa.api_E import (
    EmpresaViewSet, 
    SuscripcionViewSet, 
    RegisterView, 
    LoginView, 
    LogoutView, 
    OnPremiseViewSet, 
    ConfiguracionViewSet,
    RegisterEmpresaUserAPIView
)
 
 
router = routers.DefaultRouter()
router.register(r'empresa', EmpresaViewSet)
router.register(r'suscripcion', SuscripcionViewSet, basename='suscripcion')
router.register(r'on-premise', OnPremiseViewSet, basename='on-premise')
router.register(r'configuracion', ConfiguracionViewSet, basename='configuracion')

urlpatterns = [
    path('', include(router.urls)),

    # Ruta antigua (compatibilidad)
    path('register/empresa-user/', RegisterView.as_view(), name='register-old'),
    
    # Ruta nueva con soporte para archivos
    path('empresa/register/empresa-user/', RegisterEmpresaUserAPIView.as_view(), name='register-empresa-user'),

    path('auth/login/', LoginView.as_view(), name='login'),
 
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]