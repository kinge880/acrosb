from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.base, name='paginicial'),
    path('produtos/', views.produtos, name='produtos'),
    path('fornecs/', views.fornecedores, name='fornecedores'),
    path('campanhas/', views.campanhas, name='campanha'),
    path('campanhas/<int:idcampanha>/', views.campanhasid, name='campanhasid'),
    path('campanhas/<int:idcampanha>/<int:idclient>/', views.campanhasidclient, name='campanhasid'),
    path('sorteio/', views.sorteio, name='sorteio'),
    path('sorteio/<int:idcampanha>/', views.gerador, name='gerador'),
    path('ganhadores/<int:idcampanha>/', views.sorteioganhadores, name='ganhadores'),
    path('upload/', views.upload_planilha, name='upload_planilha'),
    path('baixar-modelo/<str:tipo>/', views.baixar_modelo, name='baixar_modelo')
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )