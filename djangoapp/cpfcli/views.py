from django.shortcuts import render
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
        codigo = request.POST.get('codigo')
        print(codigo)
        if 'delete' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEMCAMPANHA SET DTEXCLUSAO = SYSDATE 
                WHERE IDCAMPANHA = {codigo}
            ''')
            messages.success(request, f"Campanha {codigo} deletada com sucesso")
        
        elif 'desative' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEMCAMPANHA SET ATIVO = 'N' 
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
                    UPDATE MSCUPONAGEMCAMPANHA SET ATIVO = 'S' 
                    WHERE IDCAMPANHA = {codigo}
                ''')
                messages.success(request, f"Campanha {codigo} ativada com sucesso")
            else:
                messages.error(request, "Já existe uma campanha ativa, somente uma campanha ativa pode existir ao mesmo tempo")

    getTable()
    return render(request, 'campanhas/campanha.html', context)