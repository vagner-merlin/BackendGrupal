
from django.contrib import admin
from django.urls import path , include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app_Empresa.urls_E')),
    path('api/User/', include('app_User.urls')),
    path('api/Creditos/', include('app_Credito.url_Creditos')),
    path('api/Clientes/', include('app_Cliente.urls_cliente')),
]
