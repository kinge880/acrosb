from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from project.middlewares import CustomCSSMiddleware
from .models import AccessLog
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def dynamic_css(request):
    css_vars = getattr(request, 'custom_css_vars', {})
    css = render_to_string('dynamic_css.css', css_vars)
    return HttpResponse(css, content_type='text/css')

def dynamic_html(request):
    css_vars = getattr(request, 'custom_css_vars', {})
    return css_vars

def exist_campanha(cursor, idcampanha):
    cursor.execute(f'''
        SELECT IDCAMPANHA 
        FROM MSCUPONAGEMCAMPANHA 
        WHERE IDCAMPANHA = {idcampanha}
    ''')
    return cursor.fetchone()