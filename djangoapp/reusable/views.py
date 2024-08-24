from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings
from project.middlewares import CustomCSSMiddleware

# Create your views here.
def dynamic_css(request):
    css_vars = getattr(request, 'custom_css_vars', {})
    css = render_to_string('dynamic_css.css', css_vars)
    return HttpResponse(css, content_type='text/css')

def dynamic_html(request):
    css_vars = getattr(request, 'custom_css_vars', {})
    return css_vars
