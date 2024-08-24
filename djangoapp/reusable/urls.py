# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('dynamic-css/', dynamic_css, name='dynamic_css'),
    path('dynamic-css/html/', dynamic_html, name='dynamic_css_html'),
    # Outras URLs
]
