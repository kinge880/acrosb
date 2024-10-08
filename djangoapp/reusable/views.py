from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from project.middlewares import CustomCSSMiddleware
from .models import AccessLog, Agent
from django.db.models import Count
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from cpfcli.models import *
from django.middleware.csrf import get_token
from project.oracle import *
from datetime import datetime
from django.core import serializers

def divide_chunks(lst, chunk_size):
    """Divide a lista em pedaços menores de tamanho máximo chunk_size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def build_clause(field, values, in_or_not):
    """Constrói a cláusula NOT IN, incluindo divisão em chunks."""
    # Se houver apenas um item, retornar !=
    if len(values) == 1:
        if in_or_not == 'NOT':
            return f"{field} != {values[0]}"
        else:
            return f"{field} = {values[0]}"
    
    # Caso tenha mais de um item, dividir em chunks e construir várias cláusulas NOT IN
    clauses = []
    chunks = list(divide_chunks(values, 999))
    
    for chunk in chunks:
        if len(chunk) == 1:
            if in_or_not == 'NOT':
                clauses.append(f"{field} != {chunk[0]}")
            else:
                clauses.append(f"{field} = {chunk[0]}")
        else:
            if in_or_not == 'NOT':
                clauses.append(f"{field} NOT IN ({', '.join(map(str, chunk))})")
            else:
                clauses.append(f"{field} IN ({', '.join(map(str, chunk))})")
    
    # Unir todas as cláusulas com ' AND '
    return ' '.join(clauses)

def translate_column_name(column_name):
    column_translation_dict = {
        'enviaemail': 'Enviar Email',
        'acumulativo': 'Acumulativo',
        'restringe_fornec': 'Restringir Fornecedor',
        'restringe_marca': 'Restringir Marca',
        'restringe_prod': 'Restringir Produto',
        'tipointensificador': 'Tipo Intensificador',
        'usamarca': 'Uso Marca',
        'usafornec': 'Uso Fornecedor',
        'usaprod': 'Uso Produto'
    }
    return column_translation_dict.get(column_name, column_name)

def translate_value(field_name, value):
    # Dicionário de mapeamentos por campo
    translation_dict = {
        'enviaemail': {
            'N': '1 - Não enviar email',
            'S': '2 - Enviar email ao cliente informando os números da sorte obtidos'
        },
        'acumulativo': {
            'N': '1 - Não acumular saldo entre vendas',
            'S': '2 - Somente acumular saldo entre vendas com o valor total superior ao número da sorte',
            'T': '3 - Acumular saldo entre todas as vendas'
        },
        'restringe_fornec': {
            'N': '1 - Não utilizar restrição por fornecedor',
            'C': '2 - Restrição por fornecedor cadastrado'
        },
        'restringe_marca': {
            'N': '1 - Não utilizar restrição por marca',
            'C': '2 - Restrição por marca cadastrada'
        },
        'restringe_prod': {
            'N': '1 - Não utilizar restrição por produto',
            'C': '2 - Restrição por produto cadastrado'
        },
        'tipointensificador': {
            'N': '1 - Não utilizar intensificador',
            'M': '2 - Multiplicação',
            'S': '3 - Soma'
        },
        'usamarca': {
            'N': '1 - Não utilizar intensificador por marca',
            'C': '2 - Intensificador por marca cadastrada',
            'M': '3 - Intensificador por marca múltipla'
        },
        'usafornec': {
            'N': '1 - Não utilizar intensificador por fornecedor',
            'C': '2 - Intensificador por fornecedor cadastrado',
            'M': '3 - Intensificador por fornecedor múltiplo'
        },
        'usaprod': {
            'N': '1 - Não utilizar intensificador por produto',
            'C': '2 - Utilizar intensificador por produto cadastrado',
            'M': '3 - Utilizar intensificador por produto múltiplo'
        },
        'usa_numero_da_sorte': {
            'S': '1 - Deve utilizar números da sorte',
            'N': '2 - Deve utilizar cuponagem física no caixa'
        }
    }

    # Retorna o valor traduzido se existir no dicionário, caso contrário, retorna o valor original
    return translation_dict.get(field_name, {}).get(value, value)

# Create your views here.
def dynamic_css(request):
    css_vars = getattr(request, 'custom_css_vars', {})
    css = render_to_string('dynamic_css.css', css_vars)
    return HttpResponse(css, content_type='text/css')

def dynamic_html(request):
    css_vars = getattr(request, 'custom_css_vars', {})
    return css_vars

def exist_campanha(cursor, idcampanha):
    return Campanha.objects.filter(idcampanha = idcampanha).first()

def exist_marca(cursor, codmarca):
    cursor.execute(f'''
        SELECT 
            CODMARCA, 
            COALESCE(MARCA, 'Sem descrição cadastrada')
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

def exist_client_cpf_email(cursor, email, cpf_cnpj):
    cursor.execute(f'''
        SELECT 
            CODCLI, 
            COALESCE(CLIENTE, 'Sem nome cadastrado') AS CLIENTE, 
            COALESCE(EMAIL, 'Sem email cadastrado') AS EMAIL, 
            COALESCE(CGCENT, 'Sem cpf ou cnpj cadastrado') AS CGCENT
        FROM 
            PCCLIENT
        WHERE 
            (
                UPPER(EMAIL) = UPPER('{email}') OR 
                REGEXP_REPLACE(CGCENT, '[^0-9]', '') = REGEXP_REPLACE('{cpf_cnpj}', '[^0-9]', '')
            )
    ''')
    return cursor.fetchone()

def obter_cod_client(cursor, email, cpf_cnpj, conexao):
    cursor.execute(f'''
        SELECT PROXNUMCLI FROM PCCONSUM
    ''')
    numcli = cursor.fetchone()
    
    cursor.execute(f'''
        UPDATE PCCONSUM SET PROXNUMCLI = PROXNUMCLI + 1
    ''')
    conexao.commit()
    
    return numcli

def obter_praca(cursor, cidade):
    cursor.execute(f'''
        SELECT CODPRACA, PRACA FROM PCPRACA WHERE UPPER(PRACA) LIKE UPPER('%{cidade}%')
    ''')

    return cursor.fetchone()

def exist_fornec(cursor, codfornec):
    cursor.execute(f'''
        SELECT 
            CODFORNEC, 
            COALESCE(FORNECEDOR, 'Sem descrição cadastrada')
        FROM PCFORNEC
        WHERE CODFORNEC = {codfornec}
    ''')
    return cursor.fetchone()

def exist_produto(cursor, codprod):
    cursor.execute(f'''
        SELECT CODPROD,
        COALESCE(DESCRICAO, 'Sem descrição cadastrada')
        FROM PCPRODUT
        WHERE CODPROD = {codprod}
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
        print('chegou dados')
        try:
            data = json.loads(request.body)

            # Extrai os dados da requisição
            name = data.get('name')
            agent_ip = data.get('agent_ip')
            numcaixa = data.get('numcaixa', 0)
            codfilial = data.get('codfilial', 0)
            cpu_usage = data.get('cpu_usage')
            memory_usage = data.get('memory_usage')
            uptime = data.get('uptime')  # Esperado no formato de segundos
            errors_count = data.get('errors_count', 0)
            service_status = data.get('service_status')
            service_version = data.get('service_version')
            last_restart = data.get('last_restart')  # Esperado no formato 'YYYY-MM-DD HH:MM:SS'

            # Valida os dados obrigatórios
            if not name or not agent_ip:
                return JsonResponse({'error': 'Nome e IP do agente são obrigatórios'}, status=400)

            # Converte uptime de segundos para uma duração
            from datetime import timedelta
            if uptime:
                uptime = timedelta(seconds=uptime)

            # Cria ou atualiza o registro do agente
            agent, created = Agent.objects.update_or_create(
                name=name,
                agent_ip=agent_ip,
                defaults={
                    'numcaixa': numcaixa,
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'uptime': uptime,
                    'service_version': service_version,
                    'last_restart': last_restart,
                    'codfilial': codfilial
                }
            )

            return JsonResponse({'message': 'Status recebido com sucesso'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def campanha_ativa(request):
    if request.method == 'GET':
        # Filtrando campanhas ativas com data atual maior que dtinit, menor que dtfim, e dtexclusao é None
        campanhas_ativas = Campanha.objects.filter(
            ativo='S',
            dtinit__lte=datetime.now(),  # Data inicial menor ou igual ao dia atual
            dtfim__gte=datetime.now(),   # Data final maior ou igual ao dia atual
            dtexclusao = None      # dtexclusao deve ser null
        )

        # Se não houver campanhas ativas
        if not campanhas_ativas.exists():
            return JsonResponse({'message': 'Não existe campanha ativa'}, status=404)

        # Serializando os dados
        campanhas_json = serializers.serialize('json', campanhas_ativas)

        # Retornando as campanhas ativas em JSON
        return JsonResponse({'campanhas': campanhas_json}, safe=False, status=200)

def pesquisar_marca(request):
    term = request.GET.get('term')
    
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    print(term)
    if term:
        try:
            term = int(term)
            termWhere = f"WHERE MARCA LIKE '%{term}%' OR CODMARCA LIKE '%{term}%'"
        except (ValueError, TypeError):
            termWhere = f"WHERE MARCA LIKE '%{term.upper()}%'"
    else:
        termWhere = ''
        
    cursor.execute(f'''
        SELECT CODMARCA, MARCA FROM PCMARCA {termWhere}
        ORDER BY MARCA ASC
    ''')
        
    termsresult = cursor.fetchall()
    conexao.close()
    
    formatted_termsresult = [{'id': item[0], 'text': f"{item[0]} - {item[1]}"} for item in termsresult]

    import json
    return HttpResponse(json.dumps({'data': formatted_termsresult}), content_type="application/json")

def pesquisacodprodutoPCPRODUT(request):
    term = request.GET.get('term').upper()
    
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    if term:
        try:
            term = int(term)
            termWhere = f"WHERE DESCRICAO LIKE '%{term}%' OR CODPROD LIKE '%{term}%'"
        except (ValueError, TypeError):
            termWhere = f"WHERE DESCRICAO LIKE '%{term.upper()}%'"
    else:
        termWhere = ''
        
    cursor.execute(f'''
        SELECT CODPROD, DESCRICAO FROM PCPRODUT 
        {termWhere}
        ORDER BY DESCRICAO
    ''')
        
    codprod = cursor.fetchall()
    conexao.close()
    
    formatted_codprod = [{'id': item[0], 'text': f"{item[0]} - {item[1]}"} for item in codprod]
   
    import json
    return HttpResponse(json.dumps({'data': formatted_codprod}), content_type="application/json")

def pesquisafornec(request):
    term = request.GET.get('term')
    
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    if term:
        try:
            term = int(term)
            fornecWhere = f"WHERE FORNECEDOR LIKE '%{term}%' OR CODFORNEC = '{term}'"
        except (ValueError, TypeError):
            fornecWhere = f"WHERE FORNECEDOR LIKE '%{term.upper()}%'"
    else:
        fornecWhere = ''
    
    cursor.execute(f'''
        SELECT CODFORNEC, FORNECEDOR FROM PCFORNEC {fornecWhere} ORDER BY FORNECEDOR
    ''')
        
    fornec = cursor.fetchall()
    conexao.close()
    
    formatted_cat = [{'id': item[0], 'text': f"{item[0]} - {item[1]}"} for item in fornec]

    import json
    return HttpResponse(json.dumps({'data': formatted_cat}), content_type="application/json")


def pesquisacli(request):
    term = request.GET.get('term')
    
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    if term:
        try:
            term = int(term)
            pesqWhere = f"WHERE CLIENTE LIKE '%{term}%' OR CODCLI = '{term}'"
        except (ValueError, TypeError):
            pesqWhere = f"WHERE CLIENTE LIKE '%{term.upper()}%'"
    else:
        pesqWhere = ''
    
    cursor.execute(f'''
        SELECT CODCLI, CLIENTE || ' | CPF/CNPJ: ' || CGCENT FROM PCCLIENT {pesqWhere} ORDER BY CLIENTE
    ''')
        
    fornec = cursor.fetchall()
    conexao.close()
    
    formatted_cat = [{'id': item[0], 'text': f"{item[0]} - {item[1]}"} for item in fornec]

    import json
    return HttpResponse(json.dumps({'data': formatted_cat}), content_type="application/json")

def custom_404_view(request, exception):
    return render(request, 'error/404.html', status=404)

def custom_500_view(request):
    return render(request, 'error/500.html', status=500)

def custom_503_view(request):
    return render(request, 'error/503.html', status=500)