from django.shortcuts import render, redirect
from django.contrib import messages
from project.oracle import *
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test

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
                MC.DESCRICAO
            FROM MSCUPONAGEMCAMPANHA MC
                LEFT JOIN MSCUPONAGEM M ON MC.IDCAMPANHA = M.IDCAMPANHA AND M.CODCLI = {cpf_exist[1]}
            WHERE 
                MC.ATIVO = 'S'
            GROUP BY MC.DESCRICAO
        ''')
        num_da_sorte = cursor.fetchone()
        context['num_da_sorte'] = num_da_sorte
        context['cpf_exist'] = cpf_exist
            
    return render(request, 'pesquisacpf.html', context)

@login_required(login_url="/login/")
def campanhas(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Criar nova campanha'
    context['tituloEdit'] = 'Editar campanha'
    campos = [
        ['codigo', 'hidden', True, 'col-6', (), ' '],       # Código
        ['descricao', 'text', True, 'col-12', (), 'Descrição da campanha'],    # Descrição
        ['dtinicial', 'date', True, 'col-6', (), 'Data inicial da campanha'],   # Data Inicial
        ['dtfinal', 'date', True, 'col-6', (), 'Data final da campanha'],     # Data Final
        ['valor', 'number', True, 'col-6', (), 'Valor por número da sorte'],      # Valor
        ['multiplicador', 'number', False, 'col-6', (), 'Valor do multiplicador'],  # Multiplicador
        ['usafornec', 'select', True, 'col-6', (('S','Deve utilizar multiplicador por fornecedor'), ('N','Não deve utilizar multiplicador por fornecedor')), 'Valor do multiplicador'],    # USAFORNEC
        ['usaprod', 'select', True, 'col-6', (('S','Deve utilizar multiplicador por produto'), ('N','Não deve utilizar multiplicador por produto')), 'Valor do multiplicador'],      # USAPROD
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
                to_char(DTFIM, 'yyyy-mm-dd')
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
        
        if 'link' in request.POST:
            return redirect(f'/campanhas/{idcampanha}/')
        
        if 'delete' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEMCAMPANHA SET DTEXCLUSAO = SYSDATE, DTULTALT=SYSDATE
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
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMCAMPANHA
                    (IDCAMPANHA, DESCRICAO, DTULTALT, DTINIT, DTFIM, MULTIPLICADOR, VALOR, USAFORNEC, USAPROD, ATIVO)
                    VALUES((SELECT MAX(IDCAMPANHA) + 1 FROM MSCUPONAGEMCAMPANHA), '{descricao}', SYSDATE, to_date('{dtinicial}', 'yyyy-mm-dd'),
                    to_date('{dtfinal}', 'yyyy-mm-dd'), {valor}, {multiplicador}, '{usafornec}' , '{usaprod}' , 'S')
                ''')
                messages.success(request, f"Campanha inserida com sucesso")
            else:   
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMCAMPANHA
                    (IDCAMPANHA, DESCRICAO, DTULTALT, DTINIT, DTFIM, MULTIPLICADOR, VALOR, USAFORNEC, USAPROD, ATIVO)
                    VALUES((SELECT MAX(IDCAMPANHA) + 1 FROM MSCUPONAGEMCAMPANHA), '{descricao}', SYSDATE, to_date('{dtinicial}', 'yyyy-mm-dd'),
                    to_date('{dtfinal}', 'yyyy-mm-dd'), {valor}, {multiplicador}, '{usafornec}' , '{usaprod}' , 'N')
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
                    USAPROD='{usaprod}'
                WHERE IDCAMPANHA = {codigo} 
            ''')
            messages.success(request, f"Campanha {codigo} editada com sucesso")

    getTable()
    return render(request, 'campanhas/campanha.html', context)

@login_required(login_url="/login/")
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

@login_required(login_url="/login/")
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

@login_required(login_url="/login/")
def gerador(request, idcampanha):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['title'] = f'Sorteio campanha {idcampanha}'
    
    def getTable():
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
        context['numsorteado'] = cursor.fetchone()
        
        cursor.execute(f'''
            SELECT MAX(NUMSORTE), MIN(NUMSORTE)
            FROM MSCUPONAGEM
            WHERE 
                IDCAMPANHA = {idcampanha}
                AND NUMSORTE > 0
                AND CODCLI > 0
        ''')
        context['contnumsorteado'] = cursor.fetchone()

    getTable()
    return render(request, 'sorteio/gerador.html', context)