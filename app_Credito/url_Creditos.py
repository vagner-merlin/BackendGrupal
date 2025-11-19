from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_rest import CreditoViewSet, TipoCreditoViewSet
from .api import HistorialCreditoView, HistorialCreditoCIView , EstadoCreditoCIView
from .api_test import test_tipo_credito

router = DefaultRouter()
router.register(r'creditos', CreditoViewSet, basename='credito')
router.register(r'tipo-creditos', TipoCreditoViewSet, basename='tipo-credito')

urlpatterns = [
    path('', include(router.urls)),
    path('historial/', HistorialCreditoView.as_view(), name='historial-credito'),
    path('historial/<str:ci>/', HistorialCreditoCIView.as_view(), name='historial-credito-ci'),
    path('estado-credito/<str:ci>/', EstadoCreditoCIView.as_view(), name='estado-credito-ci'),
    path('test/tipos/', test_tipo_credito, name='test-tipos-credito'),
]
