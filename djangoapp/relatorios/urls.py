from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('menu/', views.menu, name='menu_relatorios'),
    path('menu/<int:codigo>/', views.menu, name='menu_relatorios_numero'),
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )