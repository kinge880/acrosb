from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib import messages
from project.oracle import *
from datetime import datetime, date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
import pandas as pd
from reusable.views import *
from reusable.models import *
from .forms import *
from acounts.models import *
from django.db import transaction
from io import BytesIO
from .models import *
from django.apps import apps
from project.conexao_postgresql import *
from django.utils import timezone
from datetime import timedelta
from .models import Cuponagem, Campanha
from django.http import JsonResponse
from django.db import models
import math

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def upload_planilha(file):
    if file:
        # Verifica a extensão do arquivo
        if not file.name.endswith(('.xls', '.xlsx')):
            return "Arquivo inválido. Por favor, envie um arquivo Excel."

        # Tenta ler o arquivo com pandas
        try:
            df = pd.read_excel(file)
            return df
        except Exception as e:
            return f'Erro ao ler o arquivo. Detalhes: {str(e)}'
    else:
        return 'Nenhum arquivo enviado.'

# View para baixar o modelo de planilha
def baixar_modelo(request, tipo):
    # Cria um DataFrame com as colunas idcampanha e codprod
    if tipo == 'P':
        df = pd.DataFrame(columns=['idcampanha', 'codprod', 'tipo'])
    elif tipo == 'F':
        df = pd.DataFrame(columns=['idcampanha', 'codfornec', 'tipo'])
    elif tipo == 'C':
        df = pd.DataFrame(columns=['idcampanha', 'codcli', 'tipo'])
    elif tipo == 'M':
        df = pd.DataFrame(columns=['idcampanha', 'codmarca', 'tipo'])
    else:
        return 'error'

    # Salva o DataFrame em um buffer
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Modelo')
    buffer.seek(0)

    # Cria a resposta HttpResponse
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=modelo_planilha.xlsx'
    return response

def validacpf(cpf):
    # Verifica se o CPF tem 11 dígitos e não é uma sequência de números iguais
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Função para calcular o dígito verificador
    def calcular_digito(cpf, pesos):
        soma = sum(int(cpf[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Verifica o primeiro dígito verificador
    pesos1 = list(range(10, 1, -1))
    digito1 = calcular_digito(cpf, pesos1)
    if int(cpf[9]) != digito1:
        return False

    # Verifica o segundo dígito verificador
    pesos2 = list(range(11, 1, -1))
    digito2 = calcular_digito(cpf, pesos2)
    if int(cpf[10]) != digito2:
        return False

    return True

def home(request):
    context = {}

    def getTable():
        print(date.today())
        # Obter campanhas que não foram excluídas (onde dtexclusao é None)
        campaigns = Campanha.objects.filter(
            dtexclusao__isnull=True,
            dtfim__gte=date.today(),
            dtinit__lte=date.today()
        ).annotate(
            count_cupons=models.Count('cuponagem__codcli', distinct=True, filter=models.Q(cuponagem__numcaixa__isnull=True)),
            count_cupomcx=models.Count('cuponagem__codcli', distinct=True, filter=models.Q(cuponagem__numcaixa__isnull=False))
        ).exclude(ativo='N')
        
        print(campaigns)

        today = now().date()  # Data atual
        processed_campaigns = []
        
        for campanha in campaigns:
            if campanha.dtfim and campanha.dtfim <= datetime.today().date() and campanha.count_cupons and campanha.count_cupons > 0 and campanha.usa_numero_da_sorte == 'S':
                # O dia atual é superior à data de término da campanha
                permite_sorteio = 'S'
            else:
                # A campanha ainda está ativa
                permite_sorteio = 'N'
            
            if campanha.usa_numero_da_sorte == 'S':
                count_cli = campanha.count_cupons
            else:
                count_cli = campanha.count_cupomcx
                
            # Criar dicionário para cada campanha
            campanha_dict = {
                'IDCAMPANHA': campanha.idcampanha,
                'DESCRICAO': campanha.descricao,
                'dtinit': campanha.dtinit,
                'dtfim': campanha.dtfim,
                'VALOR': campanha.valor,
                'MULTIPLICADOR': campanha.multiplicador,
                'USAFORNEC': campanha.usafornec,
                'USAPROD': campanha.usaprod,
                'ATIVO': campanha.ativo,
                'count_cli': count_cli,  # Contagem de cupons
                'permite_sorteio': permite_sorteio,
                'usa_numero_da_sorte': campanha.usa_numero_da_sorte,
                'logo_campanha': campanha.logo_campanha
            }

            # Calcular total de dias e dias restantes
            total_days = (campanha.dtfim - campanha.dtinit).days
            days_remaining = (campanha.dtfim - today).days
            # Calcular progresso
            if total_days > 0 and days_remaining > 0:
                progress = 100.0 - (days_remaining / total_days * 100)
            else:
                progress = 100.0

            # Adicionar dados calculados ao dicionário
            campanha_dict['total_days'] = total_days
            campanha_dict['days_remaining'] = days_remaining
            campanha_dict['progress'] = progress

            # Adicionar dicionário à lista de campanhas processadas
            processed_campaigns.append(campanha_dict)

        context['listacampanhas'] = processed_campaigns
        return render(request, 'home_page/lista_campanhas.html', context)

    getTable()
    return render(request, 'home_page/lista_campanhas.html', context)

def home_campanha(request, idcampanha):
    context = {}
    client = None
    meusnumeros = []
    context['tableOnlyView'] = True
    context['empyTable'] = 'Nenhum vencedor encontrado.'
    context['title'] = f'Lista de números da sorte na campanha {idcampanha}'
    
    # Verificando se a campanha existe e se não foi excluída
    try:
        campanha = Campanha.objects.get(idcampanha=idcampanha)
        context['campanha'] = campanha

        if campanha.dtexclusao is not None:
            messages.error(request, f'Campanha {idcampanha} não encontrada')
            return redirect('home')
    except Campanha.DoesNotExist:
        messages.error(request, f'Campanha {idcampanha} não encontrada')
        return redirect('home')

    if campanha.dtfim and campanha.dtfim >= datetime.today().date() and campanha.ativo == 'S':
        context['encerrado'] = 'N'
    else:
        context['encerrado'] = 'S'
    
    if request.method == 'POST': 
        print('iniciando POST')
        conexao = conexao_oracle()
        cursor = conexao.cursor()
        conexao_postgre = conectar_banco()
        cursor_postgre = conexao_postgre.cursor()
        numeroCupom = request.POST.get('numeroCupom')
        dataCompra = request.POST.get('dataCompra')
        valorCupom = request.POST.get('valorCupom')
        numeroCaixa = request.POST.get('numeroCaixa')
        
        cursor_postgre.execute(f'''
            SELECT 
                idcampanha, 
                descricao, 
                usafornec, 
                usaprod, 
                valor, 
                multiplicador, 
                to_char(dtinit, 'yyyy-mm-dd') AS dtinit, 
                to_char(dtfim, 'yyyy-mm-dd') AS dtfim, 
                enviaemail, 
                tipointensificador, 
                fornecvalor, 
                prodvalor, 
                acumulativo, 
                usamarca, 
                marcavalor, 
                restringe_fornec, 
                restringe_marca, 
                restringe_prod,
                (SELECT COUNT(codfilial) FROM cpfcli_campanhafilial WHERE idcampanha = cpfcli_campanha.idcampanha) AS total_filiais,
                tipo_cluster_cliente,
                acumula_intensificadores,
                autorizacao_campanha,
                regulamento,
                limite_intensificadores
            FROM 
                cpfcli_campanha
            WHERE 
                idcampanha = {idcampanha}
        ''')
        campanha_id = cursor_postgre.fetchone()

        if campanha_id is None:
            messages.error(request, f'Campanha {idcampanha} não encontrada')
            return render(request, 'home_page/campanha_editavel.html', context)
        
        cursor.execute(f'''
            SELECT 
                NUMPED,
                CODFILIAL,
                NUMCAIXA,
                VLTOTAL,
                to_char("DATA", 'yyyy-mm-dd'), 
                TO_CHAR("DATA", 'dd/mm/yyyy'),
                CODCLI
            FROM PCPEDCECF 
            WHERE 
                NUMCAIXA = {numeroCaixa} AND 
                VLTOTAL = {valorCupom} AND 
                "DATA" = to_date('{dataCompra}', 'yyyy-mm-dd') AND 
                --to_date('{dataCompra}', 'yyyy-mm-dd') BETWEEN to_date('{campanha_id[6]}', 'yyyy-mm-dd') AND to_date('{campanha_id[7]}', 'yyyy-mm-dd') AND 
                NUMCUPOM  = {numeroCupom}
        ''')
        cupom = cursor.fetchone()
        
        if cupom is None:
            messages.error(request, f'Desculpe, não foi encontrada uma venda que possua os dados do seu cupom fiscal')
            return render(request, 'home_page/campanha_editavel.html', context)
        
        # Converter as datas da campanha para objetos datetime
        campanha_dtinit = datetime.strptime(campanha_id[6], '%Y-%m-%d').date()
        campanha_dtfim = datetime.strptime(campanha_id[7], '%Y-%m-%d').date()
        cupom_data = datetime.strptime(cupom[4], '%Y-%m-%d').date()
        
        if cupom_data < campanha_dtinit:
            messages.error(request, f'Desculpe, sua compra foi realizada antes da campanha {campanha_id[1]} ter iniciado')
            return render(request, 'home_page/campanha_editavel.html', context)

        if cupom_data > campanha_dtfim:
            messages.error(request, f'Desculpe, sua compra foi realizada após a finalização da campanha {campanha_id[1]}')
            return render(request, 'home_page/campanha_editavel.html', context)
        
        cursor_postgre.execute(f'''
            SELECT codfilial 
            FROM cpfcli_campanhafilial 
            WHERE idcampanha = {idcampanha}
        ''')
        filiais = cursor_postgre.fetchall()
        lista_filiais = [str(item[0]) for item in filiais]
        
        print('cintinuando')
        """ if cupom[1] not in lista_filiais:
            messages.error(request, f'Desculpe, sua compra foi realizada em uma filial não participante da campanha! Consulte o regulamento para maiores informações.')
            return render(request, 'home_page/campanha_editavel.html', context) """

        cursor.execute(f'''
            SELECT NUMPED
            FROM MSCUPONAGEMCAMPANHAPROCESSADOS 
            WHERE 
                NUMPED = {cupom[0]} AND 
                idcampanha = {idcampanha} AND 
                CODCLI = {cupom[6]} AND 
                TRUNC(DTMOV) = to_date('{cupom[4]}', 'yyyy-mm-dd')
        ''')
        numped_exist = cursor.fetchone()
        
        if numped_exist:
            messages.warning(request, f'Opa! Parece que o seu cupom já foi processado aqui no clube, não é permitido utilizar ele novamente Ok? :)')
            return render(request, 'home_page/campanha_editavel.html', context)
        
        
        #parametros
        idcampanha = campanha_id[0]
        usa_fornec = campanha_id[2]
        usa_prod = campanha_id[3]
        valor = campanha_id[4]
        dt_inicial = campanha_id[6]
        dt_final = campanha_id[7]
        envia_email = campanha_id[8]
        tipo_intensificador = campanha_id[9]
        valor_fornecedor = campanha_id[10]
        valor_prod = campanha_id[11]
        acumulavenda = campanha_id[12]
        testa_envio_email = True
        listaprods = []
        listfornecs = []
        marcas_list = []
        lista_filiais = []
        usa_marca = campanha_id[13]
        marca_valor = campanha_id[14]
        restringe_fornec = campanha_id[15]
        restringe_marca = campanha_id[16]
        restringe_prod = campanha_id[17]
        filiais = campanha_id[18]
        cluster_cli = campanha_id[19]
        acumula_intensificador = campanha_id[20]
        autorizacao_campanha = campanha[21]
        regulamento = campanha[22]
        limite_intensificadores = campanha[23]
        
        listprods_restringe_where = ''
        marcas_restringe_Where = ''
        fornec_restringe_Where = ''
        ignora_vendas_abaixo_do_valor_cupom_having = ''
        filial_restringe_Where = ''
        blacklistWhere = ''
        
        #------------------------------------------------RESTRIÇÃO POR MARCA --------------------------------
        if restringe_marca and restringe_marca == 'C':
            cursor_postgre.execute(f'''
                select codmarca  
                from cpfcli_marcas 
                where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
            ''')
            marcas = cursor_postgre.fetchall()

            if marcas and len(marcas) > 0:
                marcas_list = [int(item[0]) for item in marcas]
                marcas_restringe_Where = build_clause("AND PCPRODUT.CODMARCA", marcas_list, 'IN')
            else:
                marcas_restringe_Where = ''
        #------------------------------------------------ INTENSIFICADOR POR PRODUTO --------------------------------
        if restringe_prod and restringe_prod == 'C':
            cursor_postgre.execute(f'''
                SELECT codprod 
                FROM cpfcli_produtos 
                where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
            ''')
            produtos = cursor_postgre.fetchall()

            if produtos and len(produtos) > 0:
                listaprods = [int(item[0]) for item in produtos]
                listprods_restringe_where = build_clause("AND PCPRODUT.CODPROD", listaprods, 'IN')
            else:
                listprods_restringe_where = ''
        #------------------------------------------------ RESTRIÇÃO POR FORNECEDOR --------------------------------
        if restringe_fornec and restringe_fornec == 'C':
            cursor_postgre.execute(f'''
                SELECT codfornec 
                FROM cpfcli_fornecedor 
                where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
            ''')
            fornecedores = cursor_postgre.fetchall()

            if fornecedores and len(fornecedores) > 0:
                listfornecs = [int(item[0]) for item in fornecedores]
                fornec_restringe_Where = build_clause("AND PCPRODUT.CODFORNEC", listfornecs, 'IN')
            else:
                fornec_restringe_Where = ''
        
        #---------------------------------------------------Restringe POR VALOR DO CUPOM ---------------------------------------------- 
        
        if acumulavenda and acumulavenda == 'S':
            ignora_vendas_abaixo_do_valor_cupom_having= f'''HAVING SUM(PCPEDI.PVENDA * PCPEDI.QT) >= {valor}'''

        #---------------------------------------------------Restringe POR FILIAL ---------------------------------------------- 
        if filiais > 0:
            cursor_postgre.execute(f'''
                SELECT codfilial 
                FROM cpfcli_campanhafilial 
                WHERE idcampanha = {idcampanha}
            ''')
            filiais = cursor_postgre.fetchall()
            
            if filiais and len(filiais) > 0:
                lista_filiais = [int(item[0]) for item in filiais]
                filial_restringe_Where = build_clause("AND PCPEDC.CODFILIAL", lista_filiais, 'IN')
            else:
                filial_restringe_Where = ''

        #------------------------------------------------ CALCULA A BLACK LIST --------------------------------
        if cluster_cli == 'B':
            cursor_postgre.execute(f'''
                select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} and tipo = 'B'
            ''')
            black_list = cursor_postgre.fetchall()
            
            if black_list and len(black_list) > 0:
                cpflist = [int(item[0]) for item in black_list]
                blacklistWhere = build_clause("AND PCPEDC.CODCLI", cpflist, 'NOT')
            else:
                blacklistWhere = ''
        
        elif cluster_cli == 'W':
            cursor_postgre.execute(f'''
                select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} and tipo = 'W'
            ''')
            black_list = cursor_postgre.fetchall()
            
            if black_list and len(black_list) > 0:
                cpflist = [int(item[0]) for item in black_list]
                blacklistWhere = build_clause("AND PCPEDC.CODCLI", cpflist, 'IN')
            else:
                blacklistWhere = ''

        #------------------------------------------------ CALCULA OS PEDIDO--------------------------------
        numpedWhere = f"AND PCPEDC.NUMPED = {cupom[0]}"
        
        cursor.execute(f'''
            SELECT 
                PCPEDC.NUMPED, 
                ROUND(SUM(PCPEDI.PVENDA * PCPEDI.QT), 2),
                TO_CHAR(PCPEDC."DATA", 'yyyy-mm-dd'), 
                PCPEDC.CODCLI,
                PCCLIENT.CLIENTE,
                PCCLIENT.EMAIL
            FROM PCPEDI 
                INNER JOIN PCPEDC ON (PCPEDC.NUMPED = PCPEDI.NUMPED)
                INNER JOIN PCPRODUT ON (PCPEDI.CODPROD = PCPRODUT.CODPROD)
                INNER JOIN PCCLIENT ON (PCPEDC.CODCLI = PCCLIENT.CODCLI)
            WHERE 
                PCPEDC."DATA" BETWEEN to_date('{dt_inicial}', 'yyyy-mm-dd') AND to_date('{dt_final}', 'yyyy-mm-dd') AND
                PCPEDC.POSICAO = 'F' AND 
                PCPEDC.ORIGEMPED IN ('F', 'T', 'R', 'B', 'A') AND
                PCPEDC.CONDVENDA != 10 AND 
                NOT EXISTS (
                    SELECT NUMPED 
                    FROM MSCUPONAGEMCAMPANHAPROCESSADOS 
                    WHERE NUMPED = PCPEDC.NUMPED 
                    AND IDCAMPANHA = {idcampanha}
                )
                {blacklistWhere}
                {numpedWhere}
                {marcas_restringe_Where}
                {listprods_restringe_where}
                {fornec_restringe_Where}
            GROUP BY PCPEDC.NUMPED, PCPEDC."DATA", PCPEDC.CODCLI, PCCLIENT.CLIENTE, PCCLIENT.EMAIL
            {ignora_vendas_abaixo_do_valor_cupom_having}
        ''')
        ped = cursor.fetchone()
        
        print(ped)
        if ped is None:
            messages.error(request, f'Poxa! Infelizmente sua compra não se qualifica para esssa campanha :(, mas não desanime ok?! Continue comprando e acumulando mais chances de vencer!')
            return render(request, 'home_page/campanha_editavel.html', context)
        
        multiplicador_cupom = campanha_id[5]
        valor_bonus = 0
        histgeracao = ''
        saldo_atual = 0
        printresult = ''
        
        #------------------------------------------------ COMEÇA A CALCULAR O SALDO --------------------------------
        if acumulavenda in ('S', 'T'):
            print('Calculando se existe saldo...')
            # Busca saldo do cliente na tabela cpfcli_cuponagemsaldo
            cursor_postgre.execute(f'''
                select saldo 
                FROM cpfcli_cuponagemsaldo 
                WHERE 
                    codcli = {ped[3]} AND 
                    idcampanha = {idcampanha}
            ''')
            saldo_cli = cursor_postgre.fetchone()

            if saldo_cli:
                saldo_atual = saldo_cli[0]
            
            # Calcula cupons
            qtcupons = int(math.floor((ped[1] + saldo_atual) / valor))
            histgeracao += f'0 - Calculou uma quantidade de {qtcupons} números'
            
            # Calcula a sobra
            sobra = (ped[1] + saldo_atual) % valor
            
            if sobra and saldo_cli:
                # Atualiza o saldo na tabela cpfcli_cuponagemsaldo
                cursor_postgre.execute(f'''
                    UPDATE cpfcli_cuponagemsaldo 
                    SET 
                        saldo = {sobra}, 
                        dtmov = NOW() 
                    WHERE 
                        codcli = {ped[3]} AND 
                        idcampanha = {idcampanha}
                ''')
                histgeracao += f'$$$1 - Calculou uma sobra de R$ {sobra}'
            
            elif sobra:
                # Insere um novo saldo na tabela cpfcli_cuponagemsaldo
                if ped[4]:
                    nomecli = ped[4].replace("'", "")
                else:
                    nomecli = ped[4]
                if ped[4]:
                    emailcli = ped[4].replace("'", "")
                else:
                    emailcli = ped[4]
                    
                cursor_postgre.execute(f'''
                    insert into cpfcli_cuponagemsaldo
                    (codcli, idcampanha, saldo, dtmov, nomecli, emailcli)
                    VALUES ({ped[3]}, {idcampanha}, {sobra}, NOW(), '{nomecli}', '{emailcli}')
                ''')
                histgeracao += f'$$$1 - Calculou uma sobra de R$ {sobra}'
            
            print('Saldo calculado...')
        
        else:
            qtcupons = int(math.floor(ped[1] / valor))
            histgeracao += f'0 - Calculou uma quantidade de {qtcupons} números'
            histgeracao += f'$$$1 - Nenhuma sobra calculada'
            print('1 - Sobra não calculada...')
        
        #----------------------------CALCULA INTENSIFICAÇÃO POR FORNECEDOR CADASTRADO ----------------------------
        if usa_fornec == 'C':
            print('Calculando se bonifica fornecedor cadastrado...')
            cursor_postgre.execute(f'''
                SELECT codfornec 
                FROM cpfcli_fornecedor 
                where idcampanha  = {idcampanha} AND tipo IN ('I')
            ''')
            fornecedores = cursor_postgre.fetchall()
            
            if fornecedores and len(fornecedores) > 0:
                listfornecsIntensifica = [int(item[0]) for item in fornecedores]
                    
                cursor.execute(f'''
                    SELECT SUM(PCPEDI.PVENDA * PCPEDI.QT), PCPRODUT.CODFORNEC
                    FROM PCPEDI
                        INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDI.NUMPED = {ped[0]}
                    GROUP BY PCPRODUT.CODFORNEC
                ''')
                valorfornecs = cursor.fetchall()

                cont = 0
                valor_acumulado = 0
                if acumula_intensificador == 'A':
                    for fornecvalue in valorfornecs:
                        if fornecvalue[1] in list(listfornecsIntensifica):
                            valor_acumulado += fornecvalue[0]
                    
                    if valor_acumulado >= valor_fornecedor:
                        qtbonus = int(math.floor(valor_acumulado / valor_fornecedor))
                        valor_bonus += (multiplicador_cupom * qtbonus)
                        cont += multiplicador_cupom
                else:
                    for fornecvalue in valorfornecs:
                        if fornecvalue[1] in list(listfornecsIntensifica):
                            if fornecvalue[0] >= valor_fornecedor:
                                valor_bonus += multiplicador_cupom
                                cont += multiplicador_cupom
                
                
                histgeracao += f'$$$2 - Aumentou o bônus de números da sorte baseado no fornecedor cadastrado em {cont}'
        
        #----------------------------CALCULA INTENSIFICAÇÃO POR FORNECEDOR MULTIPLO ----------------------------
        elif usa_fornec == 'M':
            print('Calculando se bonifica fornecedor Multiplo...')
            cursor.execute(f'''
                SELECT COUNT(DISTINCT PCPRODUT.CODFORNEC)
                FROM PCPEDI
                    INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                WHERE 
                    PCPEDI.NUMPED = {ped[0]}
            ''')
            qtfornecs = cursor.fetchone()

            cont = 0
            
            if qtfornecs[0] >= valor_fornecedor:
                valor_bonus += multiplicador_cupom
                cont += multiplicador_cupom
            
            histgeracao += f'$$$2 - Aumentou o bônus de números da sorte baseado no fornecedor multiplo em {cont}'
        
        else:
            histgeracao += f'$$$2 - Não houve bônus de números da sorte baseado no fornecedor'
            
            #----------------------------CALCULA INTENSIFICAÇÃO POR MARCA CADASTRADA ----------------------------
        if usa_marca == 'C':
            print('Calculando se bonifica MARCA cadastrado...')
            cursor_postgre.execute(f'''
                select codmarca  
                from cpfcli_marcas 
                where idcampanha  = {idcampanha} AND tipo IN ('I')
            ''')
            marcas = cursor_postgre.fetchall()

            if marcas and len(marcas) > 0:
                marcas_list_intensifica = [int(item[0]) for item in marcas]
                    
                cursor.execute(f'''
                    SELECT SUM(PCPEDI.PVENDA * PCPEDI.QT), PCPRODUT.CODMARCA
                    FROM PCPEDI
                        INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDI.NUMPED = {ped[0]}
                    GROUP BY PCPRODUT.CODMARCA
                ''')
                valor_marcas = cursor.fetchall()

                cont = 0
                valor_acumulado = 0
                if acumula_intensificador == 'A':
                    for valor in valor_marcas:
                        if valor[1] in marcas_list_intensifica:  # Ajuste aqui, removendo list()
                            valor_acumulado += valor[0]
                    
                    if valor_acumulado >= marca_valor:
                        qtbonus = int(math.floor(valor_acumulado / marca_valor))
                        valor_bonus += (multiplicador_cupom * qtbonus)
                        cont += multiplicador_cupom
                else:
                    for valor in valor_marcas:
                        if valor[1] in marcas_list_intensifica:  # Certifique-se de que marcas_list é uma lista
                            if valor[0] >= marca_valor:
                                valor_bonus += multiplicador_cupom
                                cont += multiplicador_cupom
                
                histgeracao += f'$$$3 - Aumentou o bônus de números da sorte baseado na marca cadastrada em {cont}'
        
        #----------------------------CALCULA INTENSIFICAÇÃO POR MARCA MULTIPLA ----------------------------
        elif usa_marca == 'M':
            print('Calculando se bonifica MARCA Multiplo...')
            cursor.execute(f'''
                SELECT COUNT(DISTINCT PCPRODUT.CODMARCA)
                FROM PCPEDI
                    INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                WHERE 
                    PCPEDI.NUMPED = {ped[0]}
            ''')
            qtmarcas = cursor.fetchone()

            cont = 0
            
            if qtmarcas[0] >= marca_valor:
                valor_bonus += multiplicador_cupom
                cont += multiplicador_cupom
            
            histgeracao += f'$$$3 - Aumentou o bônus de números da sorte baseado na marca multipla em {cont}'
        
        else:
            histgeracao += f'$$$3 - Não houve bônus de números da sorte baseado na marca'
            
        #----------------------------CALCULA INTENSIFICAÇÃO POR PRODUTO CADASTRADO ----------------------------
        if usa_prod == 'C':
            print('Calculando se bonifica produto cadastrado...')
            cursor_postgre.execute(f'''
                SELECT codprod 
                FROM cpfcli_produtos 
                where idcampanha  = {idcampanha} AND tipo IN ('I')
            ''')
            produtos = cursor_postgre.fetchall()

            if produtos and len(produtos) > 0:
                list_prods_intensifica = [int(item[0]) for item in produtos]
                cursor.execute(f'''
                    SELECT SUM(PCPEDI.PVENDA * PCPEDI.QT), CODPROD
                    FROM PCPEDI
                    WHERE PCPEDI.NUMPED = {ped[0]}
                    GROUP BY CODPROD
                ''')
                prodfornecs = cursor.fetchall()
                
                cont = 0
                valor_acumulado = 0
                if acumula_intensificador == 'A':
                    for prodvalue in prodfornecs:
                        if prodvalue[1] in list_prods_intensifica:
                            valor_acumulado += prodvalue[0]
                    
                    if valor_acumulado >= valor_prod:
                        qtbonus = int(math.floor(valor_acumulado / valor_prod))
                        valor_bonus += (multiplicador_cupom * qtbonus)
                        cont += multiplicador_cupom
                else:
                    for prodvalue in prodfornecs:
                        print(prodvalue)
                        print(list_prods_intensifica)
                        if prodvalue[1] in list_prods_intensifica:
                            if prodvalue[0] >= valor_prod:
                                valor_bonus += multiplicador_cupom
                                cont += multiplicador_cupom

                histgeracao += f'$$$4 - Aumentou o bônus de números da sorte baseado no produto cadastrado em {cont}'
            
        #----------------------------CALCULA INTENSIFICAÇÃO POR PRODUTO MULTIPLO ----------------------------
        elif usa_prod == 'M':
            print('Calculando se bonifica produto cadastrado...')
            cursor.execute(f'''
                SELECT COUNT(CODPROD)
                FROM PCPEDI
                WHERE PCPEDI.NUMPED = {ped[0]}
            ''')
            qtprods = cursor.fetchone()
            cont = 0
            
            if qtprods[0] >= valor_prod:
                valor_bonus += multiplicador_cupom
                cont += multiplicador_cupom

            histgeracao += f'$$$4 - Aumentou o bônus de números da sorte baseado no produto cadastrado em {cont}'
        
        else:
            histgeracao += f'$$$4 - Não houve bônus de números da sorte baseado no produto'
            
        #--------------------------------------APLICANDO BONUS NO CUPOM ORIGINAL GERAL ------------------------------------------
        if valor_bonus > 0:
            print('Calculando bonus final...')
            bonificadoWhere = 'S'
            
            if tipo_intensificador == 'M':
                oldqtd = qtcupons
                qtcupons = qtcupons * (multiplicador_cupom * valor_bonus)
                histgeracao += f'$$$5 - Multiplicou os números da sorte originais {oldqtd} números, por {multiplicador_cupom} intensificadores bonus, resultando em {qtcupons} números'
            elif tipo_intensificador == 'S':
                oldqtd = qtcupons
                qtcupons = qtcupons + (multiplicador_cupom * valor_bonus)
                histgeracao += f'$$$5 - Somou os números da sorte originais {oldqtd} números, com {multiplicador_cupom} intensificadores bonus, resultando em {qtcupons} números'
            else:
                bonificadoWhere = 'N'
        else:
            bonificadoWhere = 'N'
            histgeracao += f'$$$5 - Não foi gerado nenhum número bônus'
        
        print(qtcupons)
        cursor.execute(f'''
            SELECT CODCLI, CLIENTE, EMAIL, CGCENT, TELCOB FROM PCCLIENT WHERE CODCLI = {ped[3]}
        ''')
        client = cursor.fetchone()
        
        if client:
            codcli = client[0] if len(client) > 0 else ''
            nomecli = client[1].replace("'", "") if len(client) > 1 and client[1] else ''
            emailcli = client[2].replace("'", "") if len(client) > 2 and client[2] else ''
            cpf_cnpj = client[3].replace("'", "") if len(client) > 3 and client[3] else ''
            telcli = client[4].replace("'", "") if len(client) > 4 and client[4] else ''
                
        if qtcupons >= 1:
            for i in range(qtcupons):
                print(f'Gerando número da sorte pedido {ped[0]} volume {i + 1} de {qtcupons}')
                
                cursor_postgre.execute(f'''
                    INSERT INTO cpfcli_cuponagem
                    (id, dtmov, numped, valor, numsorte, codcli, nomecli, emailcli, telcli, cpf_cnpj, dataped, bonificado, ativo, idcampanha, numcaixa, numpedecf, tipo)
                    VALUES (
                        DEFAULT, 
                        NOW(), 
                        {ped[0]},  -- Número do pedido
                        {ped[1]},  -- Valor total
                        (SELECT COALESCE(MAX(numsorte), 0) + 1 FROM cpfcli_cuponagem WHERE idcampanha = {idcampanha} ),
                        {codcli},  -- Código do cliente
                        '{nomecli}', 
                        '{emailcli}', 
                        '{telcli}', 
                        '{cpf_cnpj}', 
                        '{ped[2]}',  -- Data do pedido
                        '{bonificadoWhere}',         -- Bonificado (ajustar conforme necessário)
                        'S',        -- Ativo
                        {idcampanha}, -- ID da campanha
                        NULL,
                        NULL,
                        'NS'
                    )
                ''')

            # Inserção em cpfcli_campanhaprocessados
            cursor_postgre.execute(f'''
                INSERT INTO cpfcli_campanhaprocessados
                (id, idcampanha, codcli, dtmov, historico, numped, geroucupom, geroubonus, tipoprocessamento)
                VALUES (
                    DEFAULT, 
                    {idcampanha},  -- ID da campanha
                    {codcli},      -- Código do cliente
                    NOW(),         -- Data de movimento
                    'S',  -- Histórico
                    {ped[0]},       -- Número do pedido
                    'S',
                    '{bonificadoWhere}',
                    'M'
                )
            ''')
            
            # Inserção em cpfcli_campanhaprocessados
            cursor.execute(f'''
                INSERT INTO MSCUPONAGEMCAMPANHAPROCESSADOS
                (NUMPED, IDCAMPANHA, DTMOV, HISTORICO, CODCLI, GEROUCUPOM, GEROUBONUS, TIPOPROCESSAMENTO)
                VALUES (
                    {ped[0]},           -- Número do pedido
                    {idcampanha},       -- ID da campanha
                    SYSDATE,              -- Data de movimento
                    'S',    -- Histórico de geração
                    {codcli},           -- Código do cliente
                    'S',                -- Gerou cupom (Sim)
                    '{bonificadoWhere}', -- Gerou bônus (Depende da condição)
                    'M'
                )
            ''')
            
            cursor_postgre.execute(f'''
                SELECT count(DISTINCT numsorte) from cpfcli_cuponagem where codcli = {ped[3]}
            ''')
            qtcupons_total = cursor_postgre.fetchone()
            
            printresult = f'Parabéns! Foi gerado {qtcupons} números da sorte :)'
            messages.success(request, printresult)
        else:
            cursor_postgre.execute(f'''
                INSERT INTO cpfcli_campanhaprocessados
                (id, idcampanha, codcli, dtmov, historico, numped, geroucupom, geroubonus, tipoprocessamento)
                VALUES (
                    DEFAULT, 
                    {idcampanha},  -- ID da campanha
                    {codcli},      -- Código do cliente
                    NOW(),         -- Data de movimento
                    'S',  -- Histórico
                    {ped[0]},       -- Número do pedido
                    'N',
                    '{bonificadoWhere}',
                    'M'
                )
            ''') 
            
            # Inserção em cpfcli_campanhaprocessados
            cursor.execute(f'''
                INSERT INTO MSCUPONAGEMCAMPANHAPROCESSADOS
                (NUMPED, IDCAMPANHA, DTMOV, HISTORICO, CODCLI, GEROUCUPOM, GEROUBONUS, TIPOPROCESSAMENTO)
                VALUES (
                    {ped[0]},           -- Número do pedido
                    {idcampanha},       -- ID da campanha
                    SYSDATE,              -- Data de movimento
                    'S',    -- Histórico de geração
                    {codcli},           -- Código do cliente
                    'N',                -- Gerou cupom (Não)
                    '{bonificadoWhere}', -- Gerou bônus (Condição)
                    'M'
                )
            ''')
            
            printresult = f'Poxa! Infelizmente seu cupon não conseguiu alcançar o valor necessário para gerar um número da sorte! Para mais informações por favor verifique o  regulamento da campanha'
            messages.error(request, printresult)
        
        conexao.commit()
        conexao_postgre.commit()
        conexao.close() 
        conexao_postgre.close()
    
    if campanha.usa_numero_da_sorte == 'S':
        # Buscando a lista de vencedores da campanha usando ORM
        vencedores = CuponagemVencedores.objects.filter(idcampanha=idcampanha, numsorte__isnull=False).select_related('numsorte', 'idcampanha')
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            meusnumeros = Cuponagem.objects.filter(idcampanha=idcampanha, numsorte__isnull=False, ativo = 'S', codcli = profile.client.codcli).select_related('idcampanha')
    else:
        vencedores = CuponagemVencedores.objects.filter(idcampanha=idcampanha, numsorte__isnull=True).select_related('numsorte', 'idcampanha')
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            meusnumeros = Cuponagem.objects.filter(idcampanha=idcampanha, numsorte__isnull=True, ativo = 'S', codcli = profile.client.codcli).select_related('idcampanha')

    context['dados'] = vencedores
    context['meus_dados'] = meusnumeros

    return render(request, 'home_page/campanha_editavel.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def get_data(request):
    id = request.GET.get('id')
    id_name = request.GET.get('id_name')
    model_name = request.GET.get('model_name')
    app_name = request.GET.get('app_name')
    transation = request.GET.get('transation')
    
    # Obtém a classe do model dinamicamente
    model = apps.get_model(app_label=app_name, model_name=model_name)
    
    # Filtra o registro pelo ID
    response = model.objects.filter(**{id_name: id}).first()

    if not response:
        return JsonResponse({'error': 'Registro não encontrado'}, status=404)
    
    response_data = {}

    # Constrói o dicionário de resposta dinamicamente
    for field in response._meta.fields:
        field_value = getattr(response, field.name)
        
        # Verifica se o campo é uma chave estrangeira
        if field.is_relation and field.many_to_one:
            # Se for uma chave estrangeira, pegar o valor relacionado (como o ID)
            related_object = getattr(response, field.name)
            field_value = related_object.pk if related_object else None
        
        # Se o campo for do tipo ImageField ou FileField, converte para URL
        elif isinstance(field, models.ImageField) or isinstance(field, models.FileField):
            field_value = field_value.url if field_value else None
        
        # Traduz o valor se necessário
        if transation == 'S':
            translated_value = translate_value(field.name, field_value)  # Aplica a tradução
            response_data[field.name] = translated_value
        else:
            response_data[field.name] = field_value
    
    return JsonResponse(response_data)

@login_required(login_url="/accounts/login/")
@staff_required
def campanhas(request):
    context = {}
    context['tituloInsere'] = 'Criar nova campanha'
    context['tituloEdit'] = 'Editar campanha'
    context['tituloDelete'] = 'Deletar a campanha'
    context['tituloActive'] = 'Ativar a campanha'
    context['tituloDeactive'] = 'Desativar a campanha'
    context['habilitaexportacaoplanilha'] = 'habilitaexportacaoplanilha'
    context['form'] = MscuponagemCampanhaForm()
    context['primarykey'] = 'idcampanha'
    context['tipoEditKey'] = 'campanha'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Campanha'
    context['nomecolum'] = 'descricao'
    context['primarykey'] = 'idcampanha'

    def getTable():
        conn = conectar_banco()
        cursor = conn.cursor()

        sql = """
        SELECT
            c.idcampanha,
            c.descricao,
            c.dtultalt,
            c.dtinit,
            c.dtfim,
            c.multiplicador,
            c.valor,
            c.usafornec,
            c.usamarca,
            c.usaprod,
            c.ativo,
            c.dtexclusao,
            c.enviaemail,
            c.tipointensificador,
            c.fornecvalor,
            c.marcavalor,
            c.prodvalor,
            c.acumulativo,
            c.restringe_fornec,
            c.restringe_marca,
            c.restringe_prod,
            STRING_AGG(cf.codfilial::TEXT, ',') AS codfiliais
        FROM
            cpfcli_campanha c
        LEFT JOIN
            cpfcli_campanhafilial cf ON c.idcampanha = cf.idcampanha
        WHERE
            c.dtexclusao IS NULL
        GROUP BY
            c.idcampanha, c.descricao, c.dtultalt, c.dtinit, c.dtfim, c.multiplicador,
            c.valor, c.usafornec, c.usamarca, c.usaprod, c.ativo, c.dtexclusao,
            c.enviaemail, c.tipointensificador, c.fornecvalor, c.marcavalor, c.prodvalor,
            c.acumulativo, c.restringe_fornec, c.restringe_marca, c.restringe_prod
        ORDER BY
            c.idcampanha;
        """

        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Mapear os resultados em um dicionário
        resultado = [dict(zip(columns, row)) for row in rows]
        
        cursor.close()
        conn.close()

        context['listacampanhas'] = resultado

    if request.method == 'POST':
        # Form data from the request
        form = MscuponagemCampanhaForm(request.POST, request.FILES)
        print(request.FILES)
        filial = request.POST.getlist('filial')
        idcampanha = request.POST.get('idcampanha')
        
        print(request.POST)
        if 'link' in request.POST:
            return redirect(f'/campanhas/{idcampanha}/')
        
        if 'delete' in request.POST and idcampanha:
            campanha = get_object_or_404(Campanha, pk=idcampanha)
            campanha.dtexclusao = timezone.now()
            campanha.ativo = 'N'
            campanha.save()
            messages.success(request, f"Campanha {campanha.idcampanha} - {campanha.descricao} deletada com sucesso")
        
        # Handle deactivation
        elif 'desative' in request.POST and idcampanha:
            campanha = get_object_or_404(Campanha, pk=idcampanha)
            campanha.ativo = 'N'
            campanha.save()
            messages.success(request, f"Campanha {campanha.idcampanha} - {campanha.descricao} desativada com sucesso")
        
        elif 'active' in request.POST and idcampanha:
            print('entrou active')
            campanha = get_object_or_404(Campanha, pk=idcampanha)
            campanha.ativo = 'S'
            campanha.save()
            messages.success(request, f"Campanha {campanha.idcampanha} - {campanha.descricao} ativada com sucesso")
        
        elif 'insert' in request.POST:
            if form.is_valid():
                # Obtenha as filiais selecionadas
                codfiliais = request.POST.getlist('filial')
                if codfiliais is None or len(codfiliais) <= 0:
                    messages.error(request, "Erro ao inserir campanha, filial não informada!") 
                else:
                    nova_campanha = form.save(commit=False)
                    nova_campanha.ativo = 'S'
                    nova_campanha.dtultalt = timezone.now()
                    nova_campanha.save()

                    # Crie registros de CuponagemCampanhaFilial para cada filial selecionada
                    CampanhaFilial.objects.bulk_create(
                        CampanhaFilial(idcampanha=nova_campanha.idcampanha, codfilial=codfilial)
                        for codfilial in codfiliais
                    )
    
                messages.success(request, "Campanha inserida com sucesso")
            else:
                error_messages = "; ".join([f"{field}: {error}" for field, errors in form.errors.items() for error in errors])
                messages.error(request, f"Erro ao editar campanha: {error_messages}")
            
        elif 'edit' in request.POST and idcampanha:
            campanha = get_object_or_404(Campanha, pk=idcampanha)
            if form.is_valid():
                with transaction.atomic():
                    for field, value in form.cleaned_data.items():
                        setattr(campanha, field, value)
                    campanha.dtultalt = timezone.now()
                    campanha.save()
                    
                    # Clear old filials and add new ones
                    CampanhaFilial.objects.filter(idcampanha=campanha.idcampanha).delete()
                    for item in filial:
                        CampanhaFilial.objects.create(idcampanha=campanha.idcampanha, codfilial=item)
                    
                    messages.success(request, f"Campanha {idcampanha} editada com sucesso")
            else:
                error_messages = "; ".join([f"{field}: {error}" for field, errors in form.errors.items() for error in errors])
                messages.error(request, f"Erro ao editar campanha: {error_messages}")

    getTable()
    return render(request, 'campanhas/campanha.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def produtos(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Adicionar produto'
    context['tituloDelete'] = 'Deletar produto'
    context['tituloPlanilha'] = 'Adicionar planilha de produtos'
    context['tipolink'] = 'P'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Produtos'
    context['nomecolum'] = 'nomeprod'
    context['primarykey'] = 'id'
    
    context['form'] = ProdutosForm()  # Usando o Django Forms
    context['habilitaexportacao'] = 'Sim'
    context['permiteplanilha'] = 'permiteplanilha'
    
    def getTable():
        context['dados'] = Produtos.objects.all()

    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codprod = request.POST.get('codprod')
        tipo = request.POST.get('tipo')
        id = request.POST.get(f"{context['primarykey']}")
        
        if 'delete' in request.POST:
            Produtos.objects.filter(id=id).delete()
            messages.success(request, f"Produto deletado com sucesso")
        
        elif 'insert' in request.POST:
            exist_test = exist_campanha(cursor, idcampanha)
            exist = exist_produto(cursor, codprod)
            
            if exist_test is None:
                getTable()
                messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                return render(request, 'cadastros/produtos.html', context)
            
            if exist is None:
                getTable()
                messages.error(request, f"O produto {codprod} não existe")
                return render(request, 'cadastros/produtos.html', context)
            
            if not Produtos.objects.filter(idcampanha=idcampanha, codprod=codprod).exists():
                Produtos.objects.create(
                    idcampanha=idcampanha,
                    codprod=codprod,
                    tipo = tipo,
                    nomeprod=exist[1],
                    dtmov = datetime.now()
                )
                messages.success(request, f"Produto {exist[1]} inserido com sucesso na campanha {exist_test.descricao}")
            else:
                messages.error(request, f"Produto {exist[1]} já cadastrado na campanha {exist_test.descricao}")
        
        elif 'insertp' in request.POST:
            file = request.FILES.get("planilhas")
            if file:
                df = upload_planilha(file)
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df)
                    return render(request, 'cadastros/produtos.html', context)
            else:
                getTable()
                messages.error(request, "Nenhuma planilha enviada")
                return render(request, 'cadastros/produtos.html', context)
            
            if not 'idcampanha' in df.columns or not 'codprod' in df.columns or not 'tipo' in df.columns:
                getTable()
                messages.error(request, "Planilha enviada no formato errado, baixe e siga o modelo padrão!")
                return render(request, 'cadastros/produtos.html', context)

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        idcampanha = row['idcampanha']
                        codprod = row['codprod']
                        tipo = row['tipo']
                        
                        exist_test = exist_campanha(cursor, idcampanha)
                        exist = exist_produto(cursor, codprod)
                        
                        if exist_test is None:
                            transaction.rollback()
                            getTable()
                            messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                            return render(request, 'cadastros/produtos.html', context)
                        
                        if exist is None:
                            getTable()
                            messages.error(request, f"O produto {codprod} não existe")
                            return render(request, 'cadastros/produtos.html', context)
                        
                        if not Produtos.objects.filter(idcampanha=idcampanha, codprod=codprod).exists():
                            Produtos.objects.create(
                                idcampanha=idcampanha,
                                codprod=codprod,
                                tipo = tipo,
                                nomeprod=exist[1],
                                dtmov = datetime.now()
                            )
                        else:
                            transaction.rollback()
                            getTable()
                            messages.error(request, f"Produto com código {codprod} já cadastrado na campanha {idcampanha}, verifique a planilha")
                            return render(request, 'cadastros/produtos.html', context)

                    messages.success(request, "Todos os produtos foram inseridos com sucesso!")

            except Exception as e:
                transaction.rollback()  # Garante que qualquer erro fará o rollback da transação
                getTable()
                messages.error(request, f"Ocorreu um erro ao processar a planilha: {str(e)}")
                return render(request, 'cadastros/produtos.html', context)
        else:
            getTable()
            messages.error(request, "Ação não reconhecida")
            return render(request, 'cadastros/produtos.html', context)

    getTable()
    return render(request, 'cadastros/produtos.html', context)

@login_required(login_url="//accounts/login/")
@staff_required
def fornecedores(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Adicionar fornecedor'
    context['tituloDelete'] = 'Deletar fornecedor'
    context['tituloPlanilha'] = 'Adicionar planilha de fornecedores'
    context['tipolink'] = 'F'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Fornecedor'
    context['nomecolum'] = 'nomefornec'
    context['primarykey'] = 'id'
    
    context['form'] = FornecedorForm()  # Usando o Django Forms
    context['habilitaexportacao'] = 'Sim'
    context['permiteplanilha'] = 'permiteplanilha'
    
    def getTable():
        context['dados'] = Fornecedor.objects.all()

    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codfornec = request.POST.get('codfornec')
        tipo = request.POST.get('tipo')
        id = request.POST.get(f"{context['primarykey']}")
        
        if 'delete' in request.POST:
            Fornecedor.objects.filter(id=id).delete()
            messages.success(request, f"Fornecedor deletado com sucesso")
        
        elif 'insert' in request.POST:
            exist_test = exist_campanha(cursor, idcampanha)
            exist = exist_fornec(cursor, codfornec)
            if exist_test is None:
                getTable()
                messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                return render(request, 'cadastros/fornecedores.html', context)
            if exist is None:
                getTable()
                messages.error(request, f"O fornecedor {codfornec} não existe")
                return render(request, 'cadastros/fornecedores.html', context)
            
            if not Fornecedor.objects.filter(idcampanha=idcampanha, codfornec=codfornec).exists():
                Fornecedor.objects.create(
                    idcampanha=idcampanha,
                    codfornec=codfornec,
                    tipo=tipo,
                    nomefornec=exist[1],
                    dtmov = datetime.now()
                )
                messages.success(request, f"Fornecedor {exist[0]} - {exist[1]} inserido com sucesso na campanha {exist_test.idcampanha} - {exist_test.descricao}")
            else:
                messages.error(request, f"Fornecedor {exist[0]} - {exist[1]} já cadastrado na campanha {exist_test.idcampanha} - {exist_test.descricao}")
        
        elif 'insertp' in request.POST:
            file = request.FILES.get("planilhas")
            if file:
                df = upload_planilha(file)
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df)
                    return render(request, 'cadastros/fornecedores.html', context)
            else:
                getTable()
                messages.error(request, "Nenhuma planilha enviada")
                return render(request, 'cadastros/fornecedores.html', context)
            
            if not 'idcampanha' in df.columns or not 'codfornec' in df.columns or not 'tipo' in df.columns:
                getTable()
                messages.error(request, "Planilha enviada no formato errado, baixe e siga o modelo padrão!")
                return render(request, 'cadastros/fornecedores.html', context)

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        idcampanha = row['idcampanha']
                        codfornec = row['codfornec']
                        tipo = row['tipo']
                        
                        exist_test = exist_campanha(cursor, idcampanha)
                        exist = exist_fornec(cursor, codfornec)
                        if exist_test is None:
                            transaction.rollback()
                            getTable()
                            messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                            return render(request, 'cadastros/fornecedores.html', context)
                        if exist is None:
                            getTable()
                            messages.error(request, f"O fornecedor {codfornec} não existe")
                            return render(request, 'cadastros/fornecedores.html', context)
            
                        if not Fornecedor.objects.filter(idcampanha=idcampanha, codfornec=codfornec).exists():
                            Fornecedor.objects.create(
                                idcampanha=idcampanha,
                                codfornec=codfornec,
                                tipo=tipo,
                                nomefornec=exist[1],
                                dtmov = datetime.now()
                            )
                        else:
                            transaction.rollback()
                            getTable()
                            messages.error(request, f"Fornecedor com código {codfornec} já cadastrado na campanha {idcampanha}, verifique a planilha")
                            return render(request, 'cadastros/fornecedores.html', context)

                    messages.success(request, "Todos os fornecedores foram inseridos com sucesso!")

            except Exception as e:
                transaction.rollback()  # Garante que qualquer erro fará o rollback da transação
                getTable()
                messages.error(request, f"Ocorreu um erro ao processar a planilha: {str(e)}")
                return render(request, 'cadastros/fornecedores.html', context)
        else:
            getTable()
            messages.error(request, "Ação não reconhecida")
            return render(request, 'cadastros/fornecedores.html', context)

    getTable()
    return render(request, 'cadastros/fornecedores.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def blacklist(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Adicionar cliente a BlackList'
    context['tituloPlanilha'] = 'Adicionar planilha de clientes a BlackList'
    context['tituloDelete'] = 'Remover cliente da BlackList'
    context['tipolink'] = 'C'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'BlackList'
    context['nomecolum'] = 'NOMECLI'
    context['primarykey'] = 'id'
    
    context['form'] = BlackListForm()
    context['habilitaexportacao'] = 'Sim'
    context['permiteplanilha'] = 'permiteplanilha'
    
    def getTable():
        context['listclis'] = BlackList.objects.all().values(
            'id', 'IDCAMPANHA', 'CODCLI', 'NOMECLI', 'EMAIL', 'CPFCNPJ', 'DTMOV', 'TIPO'
        )

    if request.method == 'POST':
        idcampanha = request.POST.get('IDCAMPANHA')
        codcli = request.POST.get('CODCLI')
        tipo = request.POST.get('TIPO')
        id = request.POST.get(f"{context['primarykey']}")
        
        if 'delete' in request.POST:
            BlackList.objects.filter(id =id).delete()
            messages.success(request, f"Cliente removido com sucesso da BlackList")
        
        elif 'insert' in request.POST:
            exist_cli = exist_client(cursor, codcli)
            exist_test = exist_campanha(cursor, idcampanha)
            
            if exist_test is None:
                getTable()
                messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                return render(request, 'cadastros/listanegra.html', context)
            
            if exist_cli is None:
                getTable()
                messages.error(request, f"Não existe cliente cadastrado com codcli {codcli}")
                return render(request, 'cadastros/listanegra.html', context)
            
            if not BlackList.objects.filter(IDCAMPANHA=idcampanha, CODCLI=codcli, TIPO = tipo).exists():
                BlackList.objects.create(
                    IDCAMPANHA=idcampanha, 
                    CODCLI = exist_cli[0], 
                    EMAIL = exist_cli[2],
                    CPFCNPJ = exist_cli[3],
                    NOMECLI = exist_cli[1],
                    DTMOV = datetime.now(),
                    TIPO = tipo
                )
                messages.success(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} inserido com sucesso na blacklist da campanha {exist_test.descricao}")
            else:
                if tipo == 'B':
                    messages.error(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} já cadastrado na BlackList da campanha {exist_test.descricao}") 
                else:
                    messages.error(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} já cadastrado na WhiteList da campanha {exist_test.descricao}") 
            
        elif 'insertp' in request.POST:
            file = request.FILES.get("planilhas")
            if file:
                df = upload_planilha(file)
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df)
                    return render(request, 'cadastros/listanegra.html', context)
            else:
                getTable()
                messages.error(request, "Nenhuma planilha enviada")
                return render(request, 'cadastros/listanegra.html', context)
            
            if not 'idcampanha' in df.columns or not 'codcli' in df.columns:
                getTable()
                messages.error(request, "Planilha enviada no formato errado")
                return render(request, 'cadastros/listanegra.html', context)

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        idcampanha = row['idcampanha']
                        codcli = row['codcli']
                        tipo = row['tipo']
                        
                        exist_cli = exist_client(cursor, codcli)
                        exist_test = exist_campanha(cursor, idcampanha)
                        
                        if exist_cli is None:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Não existe cliente cadastrado com codcli {codcli}")
                            return render(request, 'cadastros/listanegra.html', context)
            
                        if exist_test is None:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                            return render(request, 'cadastros/listanegra.html', context)
            
                        if not BlackList.objects.filter(IDCAMPANHA=idcampanha, CODCLI=codcli, TIPO = tipo).exists():
                            BlackList.objects.create(
                                IDCAMPANHA=idcampanha, 
                                CODCLI = exist_cli[0], 
                                EMAIL = exist_cli[2],
                                CPFCNPJ = exist_cli[3],
                                NOMECLI = exist_cli[1],
                                DTMOV = datetime.now(),
                                TIPO = tipo
                            )
                        else:
                            transaction.rollback() 
                            getTable()
                            if tipo == 'B':
                                messages.error(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} já cadastrado na BlackList da campanha {idcampanha}") 
                            else:
                                messages.error(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} já cadastrado na WhiteList da campanha {idcampanha}") 
                            return render(request, 'cadastros/listanegra.html', context)

                    messages.success(request, "Todos os clientes foram inseridos com sucesso!")

            except Exception as e:
                transaction.rollback()  # Garante que qualquer erro fará o rollback da transação
                getTable()
                messages.error(request, f"Ocorreu um erro ao processar a planilha: {str(e)}")
                return render(request, 'cadastros/listanegra.html', context)

        else:
            getTable()
            messages.error(request, "Ação não reconhecida")
            return render(request, 'cadastros/listanegra.html', context)

    getTable()
    return render(request, 'cadastros/listanegra.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def marcas(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Adicionar marca'
    context['tituloDelete'] = 'Deletar marca'
    context['tituloPlanilha'] = 'Adicionar planilha de marcas'
    context['tipolink'] = 'M'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Marcas'
    context['nomecolum'] = 'nomemarca'
    context['primarykey'] = 'id'
    
    context['form'] = MarcasForm()
    context['habilitaexportacao'] = 'Sim'
    context['permiteplanilha'] = 'permiteplanilha'
    
    def getTable():
        context['dados'] = Marcas.objects.all()

    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codmarca = request.POST.get('codmarca')
        tipo = request.POST.get('tipo')
        id = request.POST.get(f"{context['primarykey']}")
        
        if 'delete' in request.POST:
            Marcas.objects.filter(id =id).delete()
            messages.success(request, f"Marca deletada com sucesso")
        
        elif 'insert' in request.POST:
            exist_test = exist_campanha(cursor, idcampanha)
            exist = exist_marca(cursor, codmarca)
            if exist_test is None:
                getTable()
                messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                return render(request, 'cadastros/marcas.html', context)
            if exist is None:
                getTable()
                messages.error(request, f"A marca {codmarca} não existe")
                return render(request, 'cadastros/marcas.html', context)
            
            if not Marcas.objects.filter(idcampanha=idcampanha, codmarca=codmarca).exists():
                Marcas.objects.create(
                    idcampanha=idcampanha, 
                    codmarca=codmarca,
                    tipo=tipo,
                    nomemarca = exist[1],
                    dtmov = datetime.now()
                )
                messages.success(request, f"Marca {exist[0]} - {exist[1]} inserida com sucesso na campanha {exist_test.idcampanha} - {exist_test.descricao}")
            else:
                messages.error(request, f"Marca {exist[0]} - {exist[1]} já cadastrada na campanha {exist_test.idcampanha} - {exist_test.descricao}") 
            
        elif 'insertp' in request.POST:
            file = request.FILES.get("planilhas")
            if file:
                df = upload_planilha(file)
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df)
                    return render(request, 'cadastros/marcas.html', context)
            else:
                getTable()
                messages.error(request, "Nenhuma planilha enviada")
                return render(request, 'cadastros/marcas.html', context)
            
            if not 'idcampanha' in df.columns or not 'codmarca' in df.columns:
                getTable()
                messages.error(request, "Planilha enviada no formato errado")
                return render(request, 'cadastros/marcas.html', context)

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        idcampanha = row['idcampanha']
                        codmarca = row['codmarca']
                        tipo = row['tipo']
                        
                        exist_test = exist_campanha(cursor, idcampanha)
                        exist = exist_marca(cursor, codmarca)
                        if exist_test is None:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                            return render(request, 'cadastros/marcas.html', context)
                        if exist is None:
                            getTable()
                            messages.error(request, f"A marca {codmarca} não existe")
                            return render(request, 'cadastros/marcas.html', context)
            
                        if not Marcas.objects.filter(idcampanha=idcampanha, codmarca=codmarca).exists():
                            Marcas.objects.create(
                                idcampanha=idcampanha, 
                                codmarca=codmarca,
                                tipo = tipo,
                                nomemarca = exist[1],
                                dtmov = datetime.now()
                            )
                        else:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Marca com código {codmarca} já cadastrada na campanha {idcampanha}, verifique a planilha")
                            return render(request, 'cadastros/marcas.html', context)

                    messages.success(request, "Todas as marcas foram inseridas com sucesso!")

            except Exception as e:
                transaction.rollback()  # Garante que qualquer erro fará o rollback da transação
                getTable()
                messages.error(request, f"Ocorreu um erro ao processar a planilha: {str(e)}")
                return render(request, 'cadastros/marcas.html', context)
        else:
            getTable()
            messages.error(request, "Ação não reconhecida")
            return render(request, 'cadastros/marcas.html', context)

    getTable()
    return render(request, 'cadastros/marcas.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def campanhasid(request, idcampanha):
    context = {}
    context['tituloDelete'] = 'Deletar cliente'
    context['primarykey'] = 'codcli'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Cuponagem'
    context['nomecolum'] = 'nomecli'
    context['transation'] = 'N'
    
    # Verifica se a campanha existe
    try:
        campanha = Campanha.objects.get(idcampanha=idcampanha)
    except Campanha.DoesNotExist:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')  # Redireciona para a página de campanhas
    
    context['title'] = f'Lista de números da sorte na campanha {idcampanha}'
    
    # Verifica se a campanha foi excluída (supondo que a campanha tem um campo DTEXCLUSAO)
    if campanha.dtexclusao:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
    
    context['campanha'] = campanha
    
    def getTable():
        # Consulta usando ORM do Django
        dados = Cuponagem.objects.filter(
            idcampanha=campanha, 
            ativo='S'
        ).values('idcampanha', 'codcli', 'nomecli').annotate(total_numsorte=Count('codcli'))
        
        context['dados'] = dados

    if request.method == 'POST':
        codcli = request.POST.get('codcli')
        
        if 'delete' in request.POST:
            dados = Cuponagem.objects.filter(codcli=codcli, idcampanha=idcampanha).first()
            if dados:
                # Atualização usando ORM
                Cuponagem.objects.filter(codcli=codcli, idcampanha = idcampanha).update(ativo='N', dtmov=timezone.now())
                messages.success(request, f'Cliente {dados.codcli} - {dados.nomecli} deletado com sucesso da campanha {dados.idcampanha.descricao}')
            else:
                messages.error(request, f'Ocorreu um erro ao buscar o cliente na campanha, caso persista por favor contate o suporte')
    getTable()
    return render(request, 'campanhas/campanhaNumeros.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def campanhasidclient(request, idcampanha, idclient):
    context = {}
    context['title'] = f'Lista de números da sorte do cliente {idclient}'
    context['tituloDelete'] = 'Deletar número da sorte'
    context['primarykey'] = 'id'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Cuponagem'
    context['nomecolum'] = 'nomecli'
    context['transation'] = 'N'
    
    def getTable():
        context['dados'] = Cuponagem.objects.filter(
            idcampanha=idcampanha,
            codcli=idclient,
            ativo='S'
        ).all()
        
    try:
        campanha = Campanha.objects.get(idcampanha=idcampanha)
    except Campanha.DoesNotExist:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')
    
    if campanha.dtexclusao:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
        return redirect('campanha')
    
    if not Cuponagem.objects.filter(idcampanha=idcampanha, codcli=idclient, ativo='S').exists():
        messages.error(request, f'Não existe nenhum cupom registrado para o cliente {idclient} na campanha {idcampanha}')
        return redirect(f'/campanhas/{idcampanha}/')
    
    context['campanha'] = campanha
    context['cliente'] = f'o cliente {idclient}'
    
    if request.method == 'POST':
        id = request.POST.get('id')
        
        if 'delete' in request.POST:
            dados = Cuponagem.objects.filter(id=id, idcampanha=idcampanha).first()
            if dados:
                # Atualização usando ORM
                Cuponagem.objects.filter(id=id, idcampanha = idcampanha).update(ativo='N', dtmov=timezone.now())
                messages.success(request, f'Cliente {dados.codcli} - {dados.nomecli}, teve o seu número da sorte {dados.numsorte} deletado com sucesso da campanha {dados.idcampanha.descricao}')
            else:
                messages.error(request, f'Ocorreu um erro ao buscar o número da sorte na campanha, caso persista por favor contate o suporte')
    
    getTable()
    return render(request, 'campanhas/campanhaNumerosClient.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def campanhasidclientnumped(request, idcampanha, idclient, numped, numcaixa = ''):
    context = {}
    context['title'] = f'Lista de items no pedido {numped}'
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['numped'] = numped
    
    try:
        campanha = Campanha.objects.get(idcampanha=idcampanha)
    except Campanha.DoesNotExist:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')
    
    if campanha.dtexclusao:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
        return redirect('campanha')
    
    if not Cuponagem.objects.filter(idcampanha=idcampanha, codcli=idclient).exists():
        messages.error(request, f'Não existe nenhum cupom registrado para o cliente {idclient} na campanha {idcampanha}')
        return redirect(f'/campanhas/{idcampanha}/')
    
    context['campanha'] = campanha
    context['cliente'] = f'{idclient}'
    
    def getTable():
        if campanha.usa_numero_da_sorte == 'S':
            cursor.execute(f'''                
                SELECT 
                    PCMOV.CODPROD, 
                    PCPRODUT.CODAUXILIAR,
                    PCMOV.CODFILIAL, 
                    PCPRODUT.DESCRICAO, 
                    PCMOV.PUNIT,
                    PCMOV.QT,
                    PCPRODUT.CODFORNEC,
                    PCFORNEC.FORNECEDOR,
                    PCPRODUT.CODMARCA,
                    PCMARCA.MARCA,
                    PCMOV.DTMOV
                FROM PCMOV 
                    INNER JOIN PCPRODUT ON (PCPRODUT.CODPROD = PCMOV.CODPROD)
                    INNER JOIN PCFORNEC ON (pcprodut.codfornec = PCFORNEC.codfornec)
                    INNER JOIN PCMARCA ON (pcprodut.CODMARCA  = PCMARCA.CODMARCA)
                WHERE NUMPED = {numped}
            ''')
        elif campanha.usa_numero_da_sorte == 'N' and numcaixa:
            cursor.execute(f'''                
                SELECT PCPEDCECF.NUMPED 
                FROM PCPEDCECF 
                WHERE PCPEDCECF.NUMPEDECF = {numped} AND PCPEDCECF.NUMCAIXA = {numcaixa}
            ''')
            venda = cursor.fetchone()
            context['venda'] = venda
            if venda:
                cursor.execute(f'''                
                    SELECT 
                        PCPRODUT.CODPROD, 
                        PCPRODUT.CODAUXILIAR,
                        PCPEDC.CODFILIAL, 
                        PCPRODUT.DESCRICAO, 
                        PCPEDI.PVENDA,
                        PCPEDI.QT,
                        PCPRODUT.CODFORNEC,
                        PCFORNEC.FORNECEDOR,
                        PCPRODUT.CODMARCA,
                        PCMARCA.MARCA,
                        PCPEDI.DATA
                    FROM PCPEDI
                        INNER JOIN PCPEDC ON (PCPEDI.NUMPED = PCPEDC.NUMPED)
                        INNER JOIN PCPRODUT ON (PCPRODUT.CODPROD = PCPEDI.CODPROD)
                        INNER JOIN PCFORNEC ON (pcprodut.codfornec = PCFORNEC.codfornec)
                        INNER JOIN PCMARCA ON (pcprodut.CODMARCA  = PCMARCA.CODMARCA)
                    WHERE PCPEDC.NUMPED = {venda[0]}
                ''')
            else:
                messages.error(request, f'venda não encontrada na tabela de pedidos')
                return redirect(f'/campanhas/{idcampanha}/')
        else:
            messages.error(request, f'Campanha utiliza números da sorte, não é possivel encontrar venda por cupom')
            return redirect(f'/campanhas/{idcampanha}/')
        
        context['dados'] = cursor.fetchall()

    getTable()
    return render(request, 'campanhas/campanhaItems.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def gerador(request, idcampanha):
    context = {}
    context['title'] = f'Sorteio campanha {idcampanha}'
    
    if not Cuponagem.objects.filter(idcampanha=idcampanha).exists():
        messages.error(request, f'Nenhum cupom gerado na campanha {idcampanha}, sorteio não é possivel')
        return redirect('sorteio')
    
    # Obtem os dados gerais do sorteio
    cuponagem_sorteado = Cuponagem.objects.filter(
        idcampanha_id=idcampanha,
        ativo='S'
    ).exclude(
        codcli__in=CuponagemVencedores.objects.filter(idcampanha_id=idcampanha).values_list('codcli', flat=True)
    ).select_related('idcampanha').order_by('?').first()
    
    if cuponagem_sorteado:
        context['numsorteado'] = cuponagem_sorteado

        # Obtem o número mínimo e máximo de cupons da sorte
        numsorte_max_min = Cuponagem.objects.filter(
            idcampanha_id=idcampanha,
            ativo='S'
        ).aggregate(
            max_numsorte=models.Max('numsorte'),
            min_numsorte=models.Min('numsorte')
        )
        context['contnumsorteado'] = numsorte_max_min

        # Insere o vencedor
        CuponagemVencedores.objects.create(
            idcampanha_id=idcampanha,
            codcli=cuponagem_sorteado.codcli,
            dtsorteio=timezone.now(),
            numsorteio=CuponagemVencedores.objects.filter(idcampanha_id=idcampanha).count() + 1,
            numsorte=cuponagem_sorteado
        )

        # Obtem o número do sorteio atual
        context['numsorteio'] = CuponagemVencedores.objects.filter(
            idcampanha_id=idcampanha,
            numsorte=cuponagem_sorteado,
            codcli=cuponagem_sorteado.codcli
        ).first()
    else:
        messages.error(request, f'Não foi possivel sortear nenhum número na campanha')

    return render(request, 'sorteio/gerador.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def sorteio(request):
    context = {}

    def getTable():
        # Obter campanhas que não foram excluídas (onde dtexclusao é None)
        campaigns = Campanha.objects.filter(dtexclusao__isnull=True).annotate(
            count_cupons=models.Count('cuponagem', filter=models.Q(cuponagem__numsorte__gt=0)),
            count_cupomcx=models.Count('cuponagem', filter=models.Q(cuponagem__numcaixa__isnull=False))
        )

        today = now().date()  # Data atual
        processed_campaigns = []
        
        for campanha in campaigns:
            if campanha.dtfim and campanha.dtfim <= datetime.today().date() and campanha.count_cupons and campanha.count_cupons > 0 and campanha.usa_numero_da_sorte == 'S':
                # O dia atual é superior à data de término da campanha
                permite_sorteio = 'S'
            else:
                # A campanha ainda está ativa
                permite_sorteio = 'N'
            
            permite_sorteio = 'S'
            
            # Criar dicionário para cada campanha
            campanha_dict = {
                'IDCAMPANHA': campanha.idcampanha,
                'DESCRICAO': campanha.descricao,
                'dtinit': campanha.dtinit,
                'dtfim': campanha.dtfim,
                'VALOR': campanha.valor,
                'MULTIPLICADOR': campanha.multiplicador,
                'USAFORNEC': campanha.usafornec,
                'USAPROD': campanha.usaprod,
                'ATIVO': campanha.ativo,
                'count_cupons': campanha.count_cupons,  # Contagem de cupons
                'permite_sorteio': permite_sorteio,
                'count_cupomcx': campanha.count_cupomcx,
                'usa_numero_da_sorte': campanha.usa_numero_da_sorte
            }

            # Calcular total de dias e dias restantes
            total_days = (campanha.dtfim - campanha.dtinit).days
            days_remaining = (campanha.dtfim - today).days
            # Calcular progresso
            if total_days > 0 and days_remaining > 0:
                progress = 100.0 - (days_remaining / total_days * 100)
            else:
                progress = 100.0

            # Adicionar dados calculados ao dicionário
            campanha_dict['total_days'] = total_days
            campanha_dict['days_remaining'] = days_remaining
            campanha_dict['progress'] = progress

            # Adicionar dicionário à lista de campanhas processadas
            processed_campaigns.append(campanha_dict)

        context['listacampanhas'] = processed_campaigns
        return render(request, 'sorteio/campanhas.html', context)

    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codigo = request.POST.get('codigo')
        descricao = request.POST.get('descricao')
        dtinicial = request.POST.get('dtinicial')
        dtfinal = request.POST.get('dtfinal')
        valor = request.POST.get('valor')
        multiplicador = request.POST.get('multiplicador')
        usafornec = request.POST.get('usafornec')
        usaprod = request.POST.get('usaprod')

        if 'pesq' in request.POST:
            return redirect(f'/campanhas/{idcampanha}/')

    getTable()
    return render(request, 'sorteio/campanhas.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def sorteioganhadores(request, idcampanha):
    context = {}
    context['title'] = f'Lista de números da sorte na campanha {idcampanha}'

    # Verificando se a campanha existe e se não foi excluída
    try:
        campanha = Campanha.objects.get(idcampanha=idcampanha)
        context['campanha'] = campanha.descricao

        if campanha.dtexclusao is not None:
            messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
    except Campanha.DoesNotExist:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')

    # Buscando a lista de vencedores da campanha usando ORM
    vencedores = CuponagemVencedores.objects.filter(idcampanha=idcampanha).select_related('numsorte', 'idcampanha')

    context['dados'] = vencedores

    return render(request, 'sorteio/ganhadores.html', context)


@login_required(login_url="/accounts/login/")
@staff_required
def agent_manager(request):
    # Capturar parâmetros de filtro
    codfilial = request.GET.get('codfilial')
    agent_ip = request.GET.get('agent_ip')
    numcaixa = request.GET.get('numcaixa')
    status = request.GET.get('status')

    # Inicializa a queryset com todos os agentes
    agents = Agent.objects.all()

    # Aplica os filtros com base nos parâmetros recebidos
    if codfilial:
        agents = agents.filter(codfilial=codfilial)
    
    if agent_ip:
        agents = agents.filter(agent_ip__icontains=agent_ip)
    
    if numcaixa:
        agents = agents.filter(numcaixa__icontains=numcaixa)
    
    desactive_agents = AgentDesactive.objects.values_list('numcaixa', flat=True)
    
    now = timezone.now()
    filtered_agents = []

    # Itera pelos agentes para verificar o status e filtrar pelo status, se necessário
    for agent in agents:
        # Verifica se o agente está desativado
        if agent.numcaixa in desactive_agents:
            agent.status = "Desativado"
        else:
            # Calcula a diferença de tempo desde o último heartbeat
            last_heartbeat = agent.last_heartbeat or timezone.now()
            if now - last_heartbeat > timedelta(minutes=1):
                agent.status = "Falha"
            else:
                agent.status = "Ativo"

        # Filtrar pelo status, se o parâmetro for passado
        if status and agent.status != status:
            continue
        
        filtered_agents.append(agent)
    
    # Agrupar agentes por filial
    agents_by_filial = {}
    for agent in filtered_agents:
        if agent.codfilial not in agents_by_filial:
            agents_by_filial[agent.codfilial] = []
        agents_by_filial[agent.codfilial].append(agent)
    
    # Buscar filiais para popular o dropdown de filtro
    filiais = Agent.objects.values('codfilial').distinct()

    return render(request, 'cadastros/agent_manager.html', {
        'agents_by_filial': agents_by_filial,
        'filiais': filiais,
        'form': AgentForm(request.GET),
    })


@login_required(login_url="/accounts/login/")
@staff_required
def desativar_servico(request, numcaixa):
    if request.method == "POST":
        AgentDesactive.objects.create(numcaixa=numcaixa, dtmov=timezone.now())
    return redirect('agent_manager')

@login_required(login_url="/accounts/login/")
@staff_required
def reativar_servico(request, numcaixa):
    if request.method == "POST":
        AgentDesactive.objects.filter(numcaixa=numcaixa).delete()
    return redirect('agent_manager')