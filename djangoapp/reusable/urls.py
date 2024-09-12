# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('dynamic-css/', dynamic_css, name='dynamic_css'),
    path('dynamic-css/html/', dynamic_html, name='dynamic_css_html'),
    path('agent_status/', agent_status, name='agent_status'),
    path('get_campanha_ativa/', campanha_ativa, name='campanha_ativa'),
    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),
    # Outras URLs
]
