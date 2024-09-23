from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login/', views.login, name='login'),
    path('clientes/cadastro/', views.cadastro_cliente, name='cadastro_cliente'),
    path('config/userpage/', views.config_user_page, name='userpagepanel'),
    path('deslogar/', views.logout_view, name='logout')
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )