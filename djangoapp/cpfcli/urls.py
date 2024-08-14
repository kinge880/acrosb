from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.base, name='paginicial'),
    path('campanhas/', views.campanhas, name='campanha'),
    path('campanhas/<int:idcampanha>/', views.campanhasid, name='campanhasid'),
    path('campanhas/<int:idcampanha>/<int:idclient>/', views.campanhasidclient, name='campanhasid'),
    path('sorteio/', views.base, name='sorteio'),
    path('sorteio/<int:idcampanha>/', views.gerador, name='sorteio'),
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )