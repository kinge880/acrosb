# middlewares.py
from .oracle import *
import cx_Oracle
from django.conf import settings

class CustomCSSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.conexao = conexao_oracle()

    def __call__(self, request):
        # Adicionar a lógica para obter e armazenar as variáveis do CSS
        request.custom_css_vars = self._get_custom_css_vars()
        response = self.get_response(request)
        return response

    def _get_custom_css_vars(self):
        cursor = self.conexao.cursor()
        cursor.execute('''
            SELECT 
                backgroundFILTRO, BACKGROUNDURL, BACKGROUNDCOR, 
                TEXTOINICIAL, NAVBARLOGOTEXT, NAVBARLOGOURL
            FROM MSCUPONAGEMCONFIG
            WHERE id = 0
        ''')  # Ajuste a condição conforme necessário
        result = cursor.fetchone()
        cursor.close()
        return {
            'backgroundfiltro': result[0],
            'backgroundurl': result[1],
            'backgroundcor': result[2],
            'textoinicial': result[3],
            'navbarlogotext': result[4],
            'navbarlogourl': result[5],
        }
