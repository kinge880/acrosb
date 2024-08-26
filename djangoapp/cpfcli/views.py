from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from project.oracle import *
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
import pandas as pd
from reusable.views import *
from io import BytesIO
from django.views.decorators.http import require_http_methods

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
        df = pd.DataFrame(columns=['idcampanha', 'codprod'])
    elif tipo == 'F':
        df = pd.DataFrame(columns=['idcampanha', 'codfornec'])
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

# Create your views here.
@login_required(login_url="/accounts/login/")
def base(request):
    context = {}
    if request.method == 'POST':
        context['postmethod'] = 'sim'
        currenttime = datetime.now()
        context['currenttime'] = currenttime
        context['parametroValor'] = '100'
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        
        is_valid = validacpf(cpf)
        
        if not is_valid:
            messages.error(request, "CPF inválido")
            return render(request, 'index.html', context)
        
        conexao = conexao_oracle()
        cursor = conexao.cursor()
        
        cursor.execute(f'''
            WITH CleanedData AS (
                SELECT 
                    REGEXP_REPLACE(CGCENT, '[^0-9]', '') AS Cleaned_CGCENT, 
                    codcli, cliente, 
                    email
                FROM 
                    pcclient
            )
            SELECT 
                Cleaned_CGCENT, codcli, cliente, email
            FROM 
                CleanedData
            WHERE 
            Cleaned_CGCENT = '{cpf}' AND email = upper('{email}')
        ''')
        cpf_exist = cursor.fetchone()
        print(cpf_exist)
        
        if cpf_exist is None:
            messages.error(request, "O CPF e email informados não foram encontrados")
            context['postmethod'] = False
            return render(request, 'pesquisacpf.html', context)
        
        cursor.execute(f'''
            SELECT
                COALESCE(COUNT(DISTINCT M.numsorte), 0) AS TotalCupons,
                MC.DESCRICAO,
                MC.VALOR
            FROM MSCUPONAGEMCAMPANHA MC
                LEFT JOIN MSCUPONAGEM M ON MC.IDCAMPANHA = M.IDCAMPANHA AND M.CODCLI = {cpf_exist[1]}
            WHERE 
                MC.ATIVO = 'S'
            GROUP BY MC.DESCRICAO, MC.VALOR
        ''')
        num_da_sorte = cursor.fetchone()
        context['num_da_sorte'] = num_da_sorte
        context['cpf_exist'] = cpf_exist
            
    return render(request, 'pesquisacpf.html', context)

@login_required(login_url="/accounts/login/")
def campanhas(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Criar nova campanha'
    context['tituloEdit'] = 'Editar campanha'
    context['habilitaexportacaoplanilha'] = 'habilitaexportacaoplanilha'
    campos = [
        ['codigo', 'hidden', True, 'col-6', (), ' ', 'Codigo interno'],       # Código
        ['descricao', 'text', True, 'col-12', (), 'Nome completo da campanha', 'Descrição da campanha'],    # Descrição
        ['dtinicial', 'date', True, 'col-3', (), 'Data inicial da campanha', 'Data inicial',],   # Data Inicial
        ['dtfinal', 'date', True, 'col-3', (), 'Data final da campanha', 'Data final'],     # Data Final
        ['valor', 'number', True, 'col-3', (), 'R$', 'Valor por número'],      # Valor
        ['usaemail', 'select', True, 'col-3', 
            (
                ('N','1 - Não enviar email'),
                ('S','2 - Enviar email ao cliente informando os números da sorte obtidos'),
            ), 
            'Deve enviar email?', 
            'Envia email'
        ], 
        ['tipointensificador', 'select', True, 'col-4', 
            (
                ('N','1 - Não utilizar intensificador'),
                ('M','2 - Multiplicação'), 
                ('S','3 - Soma'),
            ), 
            'Valor do multiplicador', 
            'Tipo de intensificador'
        ],  
        [   'usafornec', 'select', True, 'col-4',
            (
                
                ('N','1 - Não utilizar intensificador por fornecedor'),
                ('C','2 - Intensificador por fornecedor cadastrado'),
                ('M','3 - Intensificador por fornecedor multiplo'),
            ),
            'Valor do multiplicador',
            'Utiliza fornecedor'
        ],  
        ['usaprod', 'select', True, 'col-4', 
            (
                
                ('N','1 - Não utilizar intensificador por produto'),
                ('C','2 - Utilizar intensificador por produto cadastrado'), 
                ('M','3 - Utilizar intensificador por produto multiplo'),
            ), 
            'Valor do multiplicador', 
            'Utiliza produto' 
        ],
        ['multiplicador', 'number', True, 'col-4', (), 'valor', 'Valor do intensificador'], 
        ['fornecvalor', 'number', True, 'col-4', (), 'Digite a quantidade', 'Quantidade de fornecedores'], 
        ['prodvalor', 'number', True, 'col-4', (), 'Digite a quantidade', 'Quantidade de produtos'], 
    ]
    context['campos'] = campos
    
    def getTable():
        cursor.execute(f'''
            SELECT 
                IDCAMPANHA, 
                DESCRICAO, 
                to_char(DTINIT, 'dd/mm/yyyy'), 
                to_char(DTFIM, 'dd/mm/yyyy'),
                VALOR,
                MULTIPLICADOR, 
                USAFORNEC, 
                USAPROD, 
                CODGANHADOR,
                GANHADOR,
                ATIVO,
                to_char(DTINIT, 'yyyy-mm-dd'),
                to_char(DTFIM, 'yyyy-mm-dd'),
                ENVIAEMAIL,
                TIPOINTENSIFICADOR,
                FORNECVALOR,
                PRODVALOR
            FROM MSCUPONAGEMCAMPANHA
            WHERE DTEXCLUSAO IS NULL
        ''')
        context['listacampanhas'] = cursor.fetchall()
    
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
        usaemail = request.POST.get('usaemail')
        tipointensificador = request.POST.get('tipointensificador')
        fornecvalor = request.POST.get('fornecvalor')
        prodvalor = request.POST.get('prodvalor')
        
        if 'link' in request.POST:
            return redirect(f'/campanhas/{idcampanha}/')
        
        if 'delete' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEMCAMPANHA SET DTEXCLUSAO = SYSDATE, DTULTALT=SYSDATE, ATIVO = 'N'
                WHERE IDCAMPANHA = {codigo}
            ''')
            messages.success(request, f"Campanha {codigo} deletada com sucesso")
        
        elif 'desative' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEMCAMPANHA SET ATIVO = 'N', DTULTALT=SYSDATE 
                WHERE IDCAMPANHA = {codigo}
            ''')
            messages.success(request, f"Campanha {codigo} desativada com sucesso")
        
        elif 'active' in request.POST:
            cursor.execute(f'''
                SELECT 
                    IDCAMPANHA
                FROM MSCUPONAGEMCAMPANHA
                WHERE ATIVO = 'S'
            ''')
            exist_active = cursor.fetchone()
            
            if exist_active is None:
                cursor.execute(f'''
                    UPDATE MSCUPONAGEMCAMPANHA SET ATIVO = 'S', DTULTALT=SYSDATE
                    WHERE IDCAMPANHA = {codigo}
                ''')
                messages.success(request, f"Campanha {codigo} ativada com sucesso")
            else:
                messages.error(request, "Já existe uma campanha ativa, somente uma campanha ativa pode existir ao mesmo tempo")
        
        elif 'insert' in request.POST:
            cursor.execute(f'''
                SELECT 
                    IDCAMPANHA
                FROM MSCUPONAGEMCAMPANHA
                WHERE ATIVO = 'S'
            ''')
            exist_active = cursor.fetchone()
                
            if exist_active is None:
                ativoWhere = 'S'
            else:
                ativoWhere = 'N'
                
            cursor.execute(f'''
                INSERT INTO MSCUPONAGEMCAMPANHA
                (
                    IDCAMPANHA, 
                    DESCRICAO, 
                    DTULTALT, 
                    DTINIT, 
                    DTFIM, 
                    MULTIPLICADOR, 
                    VALOR, 
                    USAFORNEC, 
                    USAPROD, 
                    ATIVO,
                    ENVIAEMAIL,
                    TIPOINTENSIFICADOR,
                    FORNECVALOR,
                    PRODVALOR
                )
                VALUES(
                    (
                        SELECT COALESCE(MAX(IDCAMPANHA), 0) + 1 FROM MSCUPONAGEMCAMPANHA), 
                        '{descricao}', 
                        SYSDATE, 
                        to_date('{dtinicial}', 'yyyy-mm-dd'),
                        to_date('{dtfinal}', 'yyyy-mm-dd'), 
                        {multiplicador}, 
                        {valor},
                        '{usafornec}', 
                        '{usaprod}', 
                        '{ativoWhere}',
                        '{usaemail}',
                        '{tipointensificador}',
                        '{fornecvalor}',
                        '{prodvalor}'
                        
                    )
            ''')
            messages.success(request, f"Campanha inserida com sucesso")    
        
        elif 'edit' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEMCAMPANHA
                SET  
                    DESCRICAO='{descricao}', 
                    DTULTALT=SYSDATE, 
                    DTINIT=to_date('{dtinicial}', 'yyyy-mm-dd'), 
                    DTFIM=to_date('{dtfinal}', 'yyyy-mm-dd'), 
                    MULTIPLICADOR={multiplicador}, 
                    VALOR={valor}, 
                    USAFORNEC='{usafornec}', 
                    USAPROD='{usaprod}',
                    ENVIAEMAIL = '{usaemail}',
                    TIPOINTENSIFICADOR = '{tipointensificador}',
                    FORNECVALOR = '{fornecvalor}',
                    PRODVALOR = '{prodvalor}'
                WHERE IDCAMPANHA = {codigo} 
            ''')
            messages.success(request, f"Campanha {codigo} editada com sucesso")
    
    conexao.commit()
    getTable()
    return render(request, 'campanhas/campanha.html', context)

@login_required(login_url="/accounts/login/")
def produtos(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Adicionar produto'
    context['tituloPlanilha'] = 'Adicionar planilha'
    context['tipolink'] = 'P'
    
    campos = [
        ['idcampanha', 'number', True, 'col-md-6 col-12', (), 'Código da campanha cadastrada'],       # Código
        ['codprod', 'number', True, 'col-12 col-md-6', (), 'codprod winthor 203'],    # Descrição
    ]
    context['campos'] = campos
    context['habilitaexportacao'] = 'Sim'
    context['permiteplanilha'] = 'permiteplanilha'
    
    def getTable():
        conexao.rollback()
        cursor.execute(f'''
            SELECT MSCUPONAGEMPROD.IDCAMPANHA, MSCUPONAGEMPROD.CODPROD, MSCUPONAGEMPROD.DTMOV, PCPRODUT.DESCRICAO
            FROM MSCUPONAGEMPROD 
            INNER JOIN PCPRODUT ON (MSCUPONAGEMPROD.CODPROD = PCPRODUT.CODPROD)
        ''')
        context['listprodutos'] = cursor.fetchall()
    
    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codprod = request.POST.get('codprod')
        
        if 'delete' in request.POST:
            cursor.execute(f'''
                DELETE FROM MSCUPONAGEMPROD
                WHERE IDCAMPANHA = {idcampanha} AND CODPROD = {codprod}
            ''')
            messages.success(request, f"Produto {codprod} na campanha {idcampanha} deletado com sucesso")
        
        elif 'insert' in request.POST:
            cursor.execute(f'''
                SELECT CODPROD
                FROM PCPRODUT
                WHERE CODPROD = {codprod}
            ''')
            exist_prod = cursor.fetchone()
            
            if exist_prod is None:
                messages.success(request, f"Não existe produto cadastrado no winthor com codprod {codprod}")
            
            cursor.execute(f'''
                SELECT 
                    IDCAMPANHA, CODPROD
                FROM MSCUPONAGEMPROD
                WHERE IDCAMPANHA = {idcampanha} AND CODPROD = {codprod}
            ''')
            exist_active = cursor.fetchone()
                
            if exist_active is None:
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMPROD
                    (IDCAMPANHA, CODPROD, DTMOV)
                    VALUES({idcampanha}, {codprod}, SYSDATE)
                ''')
                messages.success(request, f"Produto {codprod} inserido com sucesso na campanha {idcampanha}")
            else:   
                messages.error(request, f"Produto {codprod} já cadastrado na campanha {idcampanha}")     
        
        elif 'insertp' in request.POST:
            file = request.FILES["planilhas"]
            if file:
                df = upload_planilha(file)
                
                # Verifica se df é um DataFrame
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df) 
                    return render(request, 'produtos/produtos.html', context)
            else:
                getTable()
                messages.error(request, f"Nenhuma planilha enviada")     
                return render(request, 'produtos/produtos.html', context)
            
            if not 'idcampanha' in df.columns or not 'codprod' in df.columns:
                getTable()
                messages.error(request, f"Planilha enviada no formato errado")     
                return render(request, 'produtos/produtos.html', context)
            
            for index, row in df.iterrows():
                idcampanha = row['idcampanha']
                codprod = row['codprod']
                
                cursor.execute(f'''
                    SELECT DESCRICAO
                    FROM MSCUPONAGEMCAMPANHA 
                    WHERE 
                        IDCAMPANHA = {idcampanha}
                ''')
                exist_campanha = cursor.fetchone()
                
                if exist_campanha is None:
                    getTable()
                    messages.error(request, f"Não existe campanha cadastrada com código {idcampanha}, verifique a planilha")
                    return render(request, 'produtos/produtos.html', context)
                    
                cursor.execute(f'''
                    SELECT CODPROD
                    FROM PCPRODUT
                    WHERE CODPROD = {codprod}
                ''')
                exist_prod = cursor.fetchone()
                
                if exist_prod is None:
                    getTable()
                    messages.error(request, f"Não existe produto cadastrado no winthor com codprod {codprod}, verifique a planilha")
                    return render(request, 'produtos/produtos.html', context)
                
                cursor.execute(f'''
                    SELECT 
                        IDCAMPANHA, CODPROD
                    FROM MSCUPONAGEMPROD
                    WHERE IDCAMPANHA = {idcampanha} AND CODPROD = {codprod}
                ''')
                exist_active = cursor.fetchone()
                    
                if exist_active is None:
                    cursor.execute(f'''
                        INSERT INTO MSCUPONAGEMPROD
                        (IDCAMPANHA, CODPROD, DTMOV)
                        VALUES({idcampanha}, {codprod}, SYSDATE)
                    ''')
                else:   
                    getTable()
                    messages.error(request, f"Produto {codprod} já cadastrado na campanha {idcampanha}, verifique a planilha")  
                    return render(request, 'produtos/produtos.html', context)   
            
            messages.success(request, f"Todos os produtos foram inseridos com sucesso!")    
        conexao.commit()
    getTable()
    return render(request, 'produtos/produtos.html', context)

@login_required(login_url="/accounts/login/")
def fornecedores(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Adicionar fornecedor'
    context['tituloPlanilha'] = 'Adicionar planilha de fornecedor'
    context['tipolink'] = 'F'
    
    campos = [
        ['idcampanha', 'number', True, 'col-md-6 col-12', (), 'Código da campanha cadastrada'],       # Código
        ['codfornec', 'number', True, 'col-12 col-md-6', (), 'codfornec winthor 202'],    # Descrição
    ]
    context['campos'] = campos
    context['habilitaexportacao'] = 'Sim'
    context['permiteplanilha'] = 'permiteplanilha'
    
    def getTable():
        print('tabelou')
        conexao.rollback()
        cursor.execute(f'''
            SELECT MSCUPONAGEMFORNEC.IDCAMPANHA, MSCUPONAGEMFORNEC.CODFORNEC, MSCUPONAGEMFORNEC.DTMOV, PCFORNEC.FORNECEDOR
            FROM MSCUPONAGEMFORNEC 
            INNER JOIN PCFORNEC ON (MSCUPONAGEMFORNEC.CODFORNEC = PCFORNEC.CODFORNEC)
        ''')
        context['listfornecs'] = cursor.fetchall()
    
    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codfornec = request.POST.get('codfornec')
        
        if 'delete' in request.POST:
            cursor.execute(f'''
                DELETE FROM MSCUPONAGEMFORNEC
                WHERE IDCAMPANHA = {idcampanha} AND CODFORNEC = {codfornec}
            ''')
            messages.success(request, f"Fornecedor {codfornec} na campanha {idcampanha} deletado com sucesso")
        
        elif 'insert' in request.POST:
            cursor.execute(f'''
                SELECT CODFORNEC
                FROM PCFORNEC
                WHERE CODFORNEC = {codfornec}
            ''')
            exist_prod = cursor.fetchone()
            
            if exist_prod is None:
                messages.success(request, f"Não existe fornecedor cadastrado no winthor com codfornec {codfornec}")
            
            cursor.execute(f'''
                SELECT 
                    IDCAMPANHA, CODFORNEC
                FROM MSCUPONAGEMFORNEC
                WHERE IDCAMPANHA = {idcampanha} AND CODFORNEC = {codfornec}
            ''')
            exist_active = cursor.fetchone()
                
            if exist_active is None:
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMFORNEC
                    (IDCAMPANHA, CODFORNEC, DTMOV)
                    VALUES({idcampanha}, {codfornec}, SYSDATE)
                ''')
                messages.success(request, f"Fornecedor {codfornec} inserido com sucesso na campanha {idcampanha}")
            else:   
                messages.error(request, f"Fornecedor {codfornec} já cadastrado na campanha {idcampanha}")     
        
        elif 'insertp' in request.POST:
            file = request.FILES["planilhas"]
            if file:
                df = upload_planilha(file)
                
                # Verifica se df é um DataFrame
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df) 
                    return render(request, 'fornecedores/fornecedores.html', context)
            else:
                getTable()
                messages.error(request, f"Nenhuma planilha enviada")     
                return render(request, 'fornecedores/fornecedores.html', context)
            
            if not 'idcampanha' in df.columns or not 'codprod' in df.columns:
                getTable()
                messages.error(request, f"Planilha enviada no formato errado")     
                return render(request, 'fornecedores/fornecedores.html', context)
            
            for index, row in df.iterrows():
                idcampanha = row['idcampanha']
                codfornec = row['codfornec']
                
                cursor.execute(f'''
                    SELECT DESCRICAO
                    FROM MSCUPONAGEMCAMPANHA 
                    WHERE 
                        IDCAMPANHA = {idcampanha}
                ''')
                exist_campanha = cursor.fetchone()
                
                if exist_campanha is None:
                    getTable()
                    messages.error(request, f"Não existe campanha cadastrada com código {idcampanha}, verifique a planilha")
                    return render(request, 'produtos/produtos.html', context)
                    
                cursor.execute(f'''
                    SELECT CODFORNEC
                    FROM PCFORNEC
                    WHERE CODFORNEC = {codfornec}
                ''')
                exist_prod = cursor.fetchone()
                
                if exist_prod is None:
                    getTable()
                    messages.error(request, f"Não existe fornecedor cadastrado no winthor com codfornec {codfornec}, verifique a planilha")
                    return render(request, 'produtos/produtos.html', context)
                
                cursor.execute(f'''
                    SELECT 
                        IDCAMPANHA, CODFORNEC
                    FROM MSCUPONAGEMFORNEC
                    WHERE IDCAMPANHA = {idcampanha} AND CODFORNEC = {codfornec}
                ''')
                exist_active = cursor.fetchone()
                    
                if exist_active is None:
                    cursor.execute(f'''
                        INSERT INTO MSCUPONAGEMFORNEC
                    (IDCAMPANHA, CODFORNEC, DTMOV)
                    VALUES({idcampanha}, {codfornec}, SYSDATE)
                    ''')
                else:   
                    getTable()
                    messages.error(request, f"Fornecedor {codfornec} já cadastrado na campanha {idcampanha}, verifique a planilha")  
                    return render(request, 'produtos/produtos.html', context)   
            
            messages.success(request, f"Todos os fornecedores foram inseridos com sucesso!")    
        conexao.commit()
    getTable()
    return render(request, 'fornecedores/fornecedores.html', context)

@login_required(login_url="/accounts/login/")
def campanhasid(request, idcampanha):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['title'] = f'Lista de números da sorte na campanha {idcampanha}'
    
    cursor.execute(f'''
        SELECT 
            IDCAMPANHA, DESCRICAO
        FROM MSCUPONAGEMCAMPANHA
        WHERE idcampanha = {idcampanha}
    ''')
    exist_active = cursor.fetchone()
    
    if exist_active is None:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')
    
    cursor.execute(f'''
        SELECT 
            IDCAMPANHA, DESCRICAO
        FROM MSCUPONAGEMCAMPANHA
        WHERE idcampanha = {idcampanha} AND DTEXCLUSAO IS NOT NULL
    ''')
    exist_delete = cursor.fetchone()
    if exist_delete:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
    
    context['campanha'] = f'{exist_active[1]}'
    
    def getTable():
        cursor.execute(f'''
            SELECT 
                MSCUPONAGEM.IDCAMPANHA, 
                PCCLIENT.CODCLI, 
                PCCLIENT.CLIENTE, 
                COUNT(DISTINCT NUMSORTE)
            FROM MSCUPONAGEM 
                INNER JOIN PCCLIENT ON (pcclient.codcli = MSCUPONAGEM.codcli)
            WHERE 
                MSCUPONAGEM.IDCAMPANHA = {idcampanha} AND 
                MSCUPONAGEM.NUMSORTE > 0 AND 
                PCCLIENT.CODCLI > 0
            GROUP BY 
                PCCLIENT.CODCLI, 
                MSCUPONAGEM.IDCAMPANHA, 
                PCCLIENT.CODCLI, 
                PCCLIENT.CLIENTE
        ''')
        context['listaclients'] = cursor.fetchall()
    
    if request.method == 'POST':
        pass   

    getTable()
    return render(request, 'campanhas/campanhaNumeros.html', context)

@login_required(login_url="/accounts/login/")
def campanhasidclient(request, idcampanha, idclient):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['title'] = f'Lista de números da sorte do cliente {idclient}'
    
    cursor.execute(f'''
        SELECT 
            IDCAMPANHA, DESCRICAO
        FROM MSCUPONAGEMCAMPANHA
        WHERE idcampanha = {idcampanha}
    ''')
    exist_active = cursor.fetchone()
    
    if exist_active is None:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')
    
    cursor.execute(f'''
        SELECT 
            IDCAMPANHA, DESCRICAO
        FROM MSCUPONAGEMCAMPANHA
        WHERE idcampanha = {idcampanha} AND DTEXCLUSAO IS NOT NULL
    ''')
    exist_delete = cursor.fetchone()
    if exist_delete:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
    
    cursor.execute(f'''
        SELECT IDCAMPANHA, CODCLI
        FROM MSCUPONAGEM
        WHERE idcampanha = {idcampanha} AND codcli = {idclient}
    ''')
    exist_client = cursor.fetchone()
    
    if exist_client is None:
        messages.error(request, f'Não existe nenhum cupom registrado para o cliente {idclient} na campanha {idcampanha}')
        return redirect(f'/campanhas/{idcampanha}/')
    
    context['campanha'] = f'{exist_active[1]}'
    context['cliente'] = f'o cliente {idclient}'
    
    def getTable():
        cursor.execute(f'''
            SELECT 
                MSCUPONAGEM.IDCAMPANHA, 
                PCCLIENT.CODCLI, 
                PCCLIENT.CLIENTE,
                MSCUPONAGEM.VALOR,
                MSCUPONAGEM.NUMSORTE,
                TO_CHAR(PCPEDC."DATA", 'dd/mm/yyyy')
                
            FROM MSCUPONAGEM 
                INNER JOIN PCCLIENT ON PCCLIENT.CODCLI = MSCUPONAGEM.CODCLI
                LEFT JOIN PCPEDC ON MSCUPONAGEM.NUMPED = PCPEDC.NUMPED
            WHERE 
                MSCUPONAGEM.IDCAMPANHA = {idcampanha} AND 
                MSCUPONAGEM.NUMSORTE > 0 AND 
                PCCLIENT.CODCLI = {idclient}
        ''')
        context['listanumeros'] = cursor.fetchall()

    getTable()
    return render(request, 'campanhas/campanhaNumerosClient.html', context)

@login_required(login_url="/accounts/login/")
def gerador(request, idcampanha):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['title'] = f'Sorteio campanha {idcampanha}'
    
    def getTable():
        #obetem os dados gerais do sorteio
        cursor.execute(f'''
            SELECT NUMSORTE, SYSDATE, cliente, codcli
            FROM (
                SELECT NUMSORTE, MSCUPONAGEM.codcli, PCCLIENT.cliente
                FROM MSCUPONAGEM
                JOIN PCCLIENT ON MSCUPONAGEM.codcli = PCCLIENT.CODCLI
                WHERE MSCUPONAGEM.IDCAMPANHA = {idcampanha}
                AND MSCUPONAGEM.NUMSORTE > 0
                AND PCCLIENT.CODCLI > 0
                ORDER BY DBMS_RANDOM.VALUE
            )
            WHERE ROWNUM = 1
        ''')
        numsorte = cursor.fetchone()
        context['numsorteado'] = numsorte
        
        #obtem o numero menor e maior de cupons da sorte
        cursor.execute(f'''
            SELECT MAX(NUMSORTE), MIN(NUMSORTE)
            FROM MSCUPONAGEM
            WHERE 
                IDCAMPANHA = {idcampanha}
                AND NUMSORTE > 0
                AND CODCLI > 0
        ''')
        context['contnumsorteado'] = cursor.fetchone()
        
        #insere o vencedor
        cursor.execute(f'''
            INSERT INTO MSCUPONAGEMVENCEDORES
            (IDCAMPANHA, CODCLI, DTSORTEIO, NUMSORTEIO, NUMSORTE)
            VALUES(
                {idcampanha}, 
                {numsorte[3]}, 
                SYSDATE, 
                (
                    select count(numsorte)
                    from MSCUPONAGEMVENCEDORES 
                    where 
                        idcampanha = {idcampanha}
                ) + 1, 
                {numsorte[0]}
            )
        ''')
        
        conexao.commit()
        
        #obtem o numero do sorteio atual
        cursor.execute(f'''
            SELECT NUMSORTEIO
            FROM MSCUPONAGEMVENCEDORES
            WHERE 
                IDCAMPANHA = {idcampanha} AND
                NUMSORTE = {numsorte[0]} AND
                CODCLI = {numsorte[3]}
        ''')
        context['numsorteio'] = cursor.fetchone()

    getTable()
    return render(request, 'sorteio/gerador.html', context)


@login_required(login_url="/accounts/login/")
def sorteio(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    def getTable():
        cursor.execute(f'''
            SELECT 
                IDCAMPANHA, 
                DESCRICAO, 
                to_char(DTINIT, 'dd/mm/yyyy'), 
                to_char(DTFIM, 'dd/mm/yyyy'),
                VALOR,
                MULTIPLICADOR, 
                USAFORNEC, 
                USAPROD, 
                CODGANHADOR,
                GANHADOR,
                ATIVO,
                to_char(DTINIT, 'yyyy-mm-dd'),
                to_char(DTFIM, 'yyyy-mm-dd'),
                (SELECT COUNT(NUMSORTE) FROM MSCUPONAGEM WHERE IDCAMPANHA = MSCUPONAGEMCAMPANHA.IDCAMPANHA)
            FROM MSCUPONAGEMCAMPANHA
            WHERE DTEXCLUSAO IS NULL
        ''')
        listacampanhas = cursor.fetchall()
        # Supondo que você tenha uma função para obter campanhas
        campaigns = listacampanhas  # Substitua por sua lógica real de obtenção de campanhas

        today = now().date()  # Obtém a data atual como datetime.date
        processed_campaigns = []
        for campanha in campaigns:
            # Criar dicionário para cada campanha
            campanha_dict = {
                'IDCAMPANHA': campanha[0],
                'DESCRICAO': campanha[1],
                'dtinit': datetime.strptime(campanha[11], '%Y-%m-%d').date(),
                'dtfim': datetime.strptime(campanha[12], '%Y-%m-%d').date(),
                'VALOR': campanha[4],
                'MULTIPLICADOR': campanha[5],
                'USAFORNEC': campanha[6],
                'USAPROD': campanha[7],
                'CODGANHADOR': campanha[8],
                'GANHADOR': campanha[9],
                'ATIVO': campanha[10],
                'count_cupons': campanha[13],
            }

            # Calcular total de dias e dias restantes
            total_days = (campanha_dict['dtfim'] - campanha_dict['dtinit']).days
            days_remaining = (campanha_dict['dtfim'] - today).days
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

        context ['listacampanhas'] = processed_campaigns
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
def sorteioganhadores(request, idcampanha):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['title'] = f'Lista de números da sorte na campanha {idcampanha}'
    
    cursor.execute(f'''
        SELECT 
            IDCAMPANHA, DESCRICAO
        FROM MSCUPONAGEMCAMPANHA
        WHERE idcampanha = {idcampanha}
    ''')
    exist_active = cursor.fetchone()
    
    if exist_active is None:
        messages.error(request, f'Campanha {idcampanha} não encontrada no sistema')
        return redirect('campanha')
    
    cursor.execute(f'''
        SELECT 
            IDCAMPANHA, DESCRICAO
        FROM MSCUPONAGEMCAMPANHA
        WHERE idcampanha = {idcampanha} AND DTEXCLUSAO IS NOT NULL
    ''')
    exist_delete = cursor.fetchone()
    if exist_delete:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
    
    context['campanha'] = f'{exist_active[1]}'
    
    def getTable():
        cursor.execute(f'''
            SELECT 
                MSCUPONAGEMVENCEDORES.IDCAMPANHA, 
                MSCUPONAGEMVENCEDORES.NUMSORTEIO,
                PCCLIENT.CODCLI, 
                PCCLIENT.CLIENTE, 
                MSCUPONAGEMVENCEDORES.NUMSORTE,
                MSCUPONAGEMVENCEDORES.DTSORTEIO,
                PCCLIENT.EMAIL,
                PCCLIENT.TELCOB,
                PCCLIENT.CGCENT
            FROM MSCUPONAGEMCAMPANHA 
                INNER JOIN MSCUPONAGEMVENCEDORES ON (MSCUPONAGEMCAMPANHA.IDCAMPANHA = MSCUPONAGEMVENCEDORES.IDCAMPANHA)
                INNER JOIN PCCLIENT ON (pcclient.codcli = MSCUPONAGEMVENCEDORES.codcli)
            WHERE 
                MSCUPONAGEMCAMPANHA.IDCAMPANHA = {idcampanha}
            ORDER BY 
                MSCUPONAGEMVENCEDORES.NUMSORTE
        ''')
        context['listaclients'] = cursor.fetchall()
    
    if request.method == 'POST':
        pass   

    getTable()
    return render(request, 'sorteio/ganhadores.html', context)