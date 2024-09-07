from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from project.middlewares import CustomCSSMiddleware
from .models import AccessLog
from django.db.models import Count
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.middleware.csrf import get_token
from project.oracle import *

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
        SELECT IDCAMPANHA, DESCRICAO 
        FROM MSCUPONAGEMCAMPANHA 
        WHERE IDCAMPANHA = {idcampanha}
    ''')
    return cursor.fetchone()

def exist_marca(cursor, codmarca):
    cursor.execute(f'''
        SELECT 
            CODMARCA, 
            MARCA  
        FROM pcmarca 
        WHERE CODMARCA = {codmarca}
    ''')
    return cursor.fetchone()

def exist_client(cursor, codcli):
    cursor.execute(f'''
        SELECT 
            CODCLI, 
            COALESCE(CLIENTE, 'Sem nome cadastrado'), 
            COALESCE(EMAIL, 'Sem email cadastrado'), 
            COALESCE(CGCENT, 'Sem cpf ou cnpj cadastrado')
        FROM PCCLIENT
        WHERE CODCLI = {codcli}
    ''')
    return cursor.fetchone()

def obter_filiais():
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    cursor.execute(f'''
        SELECT codigo, RAZAOSOCIAL FROM pcfilial order by codigo asc
    ''')
    filiais = cursor.fetchall()
    conexao.close()
    
    return filiais


def obter_choices_filiais():
    # Aqui chamamos o método que retorna a lista de filiais no formato (codigo, descricao)
    filiais = obter_filiais()

    # Adicionar uma opção em branco (opcional)
    choices = [(filial[0], f'{filial[0]} - {filial[1]}') for filial in filiais]
    
    return choices
    
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

@csrf_exempt
def agent_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupons_generated = data.get('coupons_generated')
            agent_ip = data.get('agent_ip')
            name = data.get('name')
            # Aqui você pode processar e armazenar os dados no banco de dados
            # Exemplo: salvar no modelo AgentStatus

            return JsonResponse({'message': 'Status recebido com sucesso'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)