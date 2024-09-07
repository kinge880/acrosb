from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.base, name='paginicial'),
    path('clientes/cadastro/', views.cadastro_cliente, name='cadastro_cliente'),
    path('produtos/', views.produtos, name='produtos'),
    path('blacklist/', views.blacklist, name='blacklist'),
    path('fornecs/', views.fornecedores, name='fornecedores'),
    path('marcas/', views.marcas, name='marcas'),
    path('campanhas/', views.campanhas, name='campanha'),
    path('campanhas/<int:idcampanha>/', views.campanhasid, name='campanhasid'),
    path('campanhas/<int:idcampanha>/<int:idclient>/', views.campanhasidclient, name='campanhasid'),
    path('campanhas/<int:idcampanha>/<int:idclient>/<int:numped>/', views.campanhasidclientnumped, name='campanhasidclientnumped'),
    path('sorteio/', views.sorteio, name='sorteio'),
    path('sorteio/<int:idcampanha>/', views.gerador, name='gerador'),
    path('ganhadores/<int:idcampanha>/', views.sorteioganhadores, name='ganhadores'),
    path('upload/', views.upload_planilha, name='upload_planilha'),
    path('get_data_edit/', views.get_data_edit, name='get_data_edit'),
    path('get_data_delete/', views.get_data_delete, name='get_data_delete'),
    path('baixar-modelo/<str:tipo>/', views.baixar_modelo, name='baixar_modelo')
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )