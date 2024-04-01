from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

route = routers.DefaultRouter()

urlpatterns = [
    path('', include(route.urls)),
    path('usuario/resetar_senha/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]  

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
    )