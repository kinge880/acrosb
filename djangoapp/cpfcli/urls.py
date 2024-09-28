from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('campanha/<int:idcampanha>/', views.home_campanha, name='home_campanha'),
    path('produtos/', views.produtos, name='produtos'),
    path('blacklist/', views.blacklist, name='blacklist'),
    path('gerenciamento/agentes/', views.agent_manager, name='agent_manager'),
    path('gerenciamento/agentes/desativar/<int:numcaixa>/', views.desativar_servico, name='desativar_servico'),
    path('gerenciamento/agentes/reativar/<int:numcaixa>/', views.reativar_servico, name='reativar_servico'),
    path('fornecs/', views.fornecedores, name='fornecedores'),
    path('marcas/', views.marcas, name='marcas'),
    path('campanhas/', views.campanhas, name='campanha'),
    path('campanhas/<int:idcampanha>/', views.campanhasid, name='campanhasid'),
    path('campanhas/<int:idcampanha>/<int:idclient>/', views.campanhasidclient, name='campanhasid'),
    path('campanhas/<int:idcampanha>/<int:idclient>/<int:numped>/', views.campanhasidclientnumped, name='campanhasidclientnumped'),
    path('campanhas/<int:idcampanha>/<int:idclient>/<int:numped>/<int:numped>', views.campanhasidclientnumped, name='campanhasidclientnumped'),
    path('sorteio/', views.sorteio, name='sorteio'),
    path('sorteio/<int:idcampanha>/', views.gerador, name='gerador'),
    path('ganhadores/<int:idcampanha>/', views.sorteioganhadores, name='ganhadores'),
    path('upload/', views.upload_planilha, name='upload_planilha'),
    path('get_data/', views.get_data, name='get_data_dict'),
    path('baixar-modelo/<str:tipo>/', views.baixar_modelo, name='baixar_modelo')
] 

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )