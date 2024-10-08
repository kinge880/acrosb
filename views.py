from django.shortcuts import render, redirect, HttpResponse
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib import messages
from project.oracle import *
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
import pandas as pd
from reusable.views import *
from .forms import *
from django.db import transaction
from io import BytesIO
from django.views.decorators.http import require_http_methods
from .models import *
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

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
        df = pd.DataFrame(columns=['idcampanha', 'codcli'])
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

def base(request):
    context = {}
    if request.method == 'POST':
        context['postmethod'] = True
        currenttime = datetime.now()
        context['currenttime'] = currenttime
        context['parametroValor'] = '100'
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
                
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
            Cleaned_CGCENT = '{cpf}' AND upper(email) = upper('{email}')
        ''')
        cpf_exist = cursor.fetchone()
        print(cpf_exist)
        
        if cpf_exist is None:
            messages.error(request, "O CPF e email informados não foram encontrados")
            context['postmethod'] = False
            return render(request, 'pesquisacpf.html', context)
        
        cursor.execute(f'''
            SELECT
                IDCAMPANHA
            FROM MSCUPONAGEMCAMPANHA
            WHERE 
                ATIVO = 'S'
        ''')
        campanha_ativa = cursor.fetchone()
        
        if campanha_ativa is None:
            messages.warning(request, "Atualmente não existe nenhuma campanha promocional ativa no sistema")
            context['postmethod'] = False
            return render(request, 'pesquisacpf.html', context)
        
       	cursor.execute(f'''
            SELECT
                M.numsorte,
                MC.DESCRICAO,
                MC.VALOR,
                M.DATAPED
            FROM MSCUPONAGEMCAMPANHA MC
                LEFT JOIN MSCUPONAGEM M ON MC.IDCAMPANHA = M.IDCAMPANHA AND M.CODCLI = {cpf_exist[1]}
            WHERE 
                MC.ATIVO = 'S'
        ''')
        num_da_sorte = cursor.fetchall()
        context['num_da_sorte'] = num_da_sorte
        context['cpf_exist'] = cpf_exist
            
    return render(request, 'pesquisacpf.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def get_data_delete(request):
    id = request.GET.get('id')
    model_name = request.GET.get('model_name')
    app_name = request.GET.get('app_name')
    
    try:
        # Obtém a classe do model dinamicamente
        model = apps.get_model(app_label=app_name, model_name=model_name)
        
        # Filtra o registro pelo ID
        response = model.objects.filter(id=id).first()

        if not response:
            return JsonResponse({'error': 'Registro não encontrado'}, status=404)

        # Constrói o dicionário de resposta dinamicamente
        response_data = {field.name: getattr(response, field.name) for field in response._meta.fields}
        
        return JsonResponse(response_data)
    except LookupError:
        return JsonResponse({'error': 'Model não encontrada'}, status=400)

@login_required(login_url="/accounts/login/")
@staff_required
def get_data_edit(request):
    id = request.GET.get('id')
    tipo = request.GET.get('tipo')
    
    if tipo == 'campanha':
        conexao = conexao_oracle()
        cursor = conexao.cursor()
        cursor.execute(f'''
            SELECT 
                IDCAMPANHA, DESCRICAO, DTINIT, DTFIM, VALOR, MULTIPLICADOR, 
                USAFORNEC, USAPROD, ENVIAEMAIL, TIPOINTENSIFICADOR, 
                FORNECVALOR, PRODVALOR, ACUMULATIVO, MARCAVALOR, USAMARCA, 
                RESTRINGE_FORNEC, RESTRINGE_MARCA, RESTRINGE_PROD 
            FROM MSCUPONAGEMCAMPANHA 
            WHERE IDCAMPANHA = {id}
        ''')
        data = cursor.fetchone()
        
        cursor.execute(f'''
            SELECT CODFILIAL
            FROM MSCUPONAGEMCAMPANHAFILIAL 
            WHERE IDCAMPANHA = {id}
        ''')
        filiais = cursor.fetchall()
        listfilial = []
        
        if len(filiais) > 0:
            for item in filiais:
                listfilial.extend(item)
            
        response_data = {
            'idcampanha': data[0],
            'descricao': data[1],
            'dtinit': data[2],
            'dtfim': data[3],
            'valor': data[4],
            'multiplicador': data[5],
            'usafornec': data[6],
            'usaprod': data[7],
            'enviaemail': data[8],
            'tipointensificador': data[9],
            'fornecvalor': data[10],
            'prodvalor': data[11],
            'acumulativo': data[12],
            'marcavalor': data[13],
            'usamarca': data[14],
            'restringe_fornec': data[15],
            'restringe_marca': data[16],
            'restringe_prod': data[17],
            'filial': listfilial
        }
        conexao.close()
        
    return JsonResponse(response_data)

@login_required(login_url="/accounts/login/")
@staff_required
def campanhas(request):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['tituloInsere'] = 'Criar nova campanha'
    context['tituloEdit'] = 'Editar campanha'
    context['habilitaexportacaoplanilha'] = 'habilitaexportacaoplanilha'
    context['form'] = MscuponagemCampanhaForm()
    context['primarykey'] = 'idcampanha'
    context['tipoEditKey'] = 'campanha'

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
                PRODVALOR,
                ACUMULATIVO,
                MARCAVALOR,
                USAMARCA,
                RESTRINGE_FORNEC,
                RESTRINGE_MARCA,
                RESTRINGE_PROD
            FROM MSCUPONAGEMCAMPANHA
            WHERE DTEXCLUSAO IS NULL
        ''')
        context['listacampanhas'] = cursor.fetchall()
    
    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codigo = request.POST.get('idcampanha')
        descricao = request.POST.get('descricao')
        dtinicial = request.POST.get('dtinit')
        dtfinal = request.POST.get('dtfim')
        valor = request.POST.get('valor')
        multiplicador = request.POST.get('multiplicador')
        usafornec = request.POST.get('usafornec')
        usaprod = request.POST.get('usaprod')
        usaemail = request.POST.get('enviaemail')
        tipointensificador = request.POST.get('tipointensificador')
        fornecvalor = request.POST.get('fornecvalor')
        prodvalor = request.POST.get('prodvalor')
        marcavalor = request.POST.get('marcavalor')
        usamarca = request.POST.get('usamarca')
        restringe_fornec = request.POST.get('restringe_fornec')
        restringe_marca = request.POST.get('restringe_marca')
        restringe_prod = request.POST.get('restringe_prod')
        acumulativo = request.POST.get('acumulativo')
        filial = request.POST.getlist('filial')
        
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
                    PRODVALOR,
                    MARCAVALOR,
                    USAMARCA,
                    RESTRINGE_FORNEC,
                    RESTRINGE_MARCA,
                    RESTRINGE_PROD,
                    ACUMULATIVO
                )
                VALUES(
                    (
                        SELECT COALESCE(MAX(IDCAMPANHA), 0) + 1 FROM MSCUPONAGEMCAMPANHA
                    ), 
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
                    {fornecvalor},
                    {prodvalor},
                    {marcavalor},
                    '{usamarca}',
                    '{restringe_fornec}',
                    '{restringe_marca}',
                    '{restringe_prod}',
                    '{acumulativo}'
                )
            ''')
            
            for item in filial:
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMCAMPANHAFILIAL
                    (
                        IDCAMPANHA, 
                        CODFILIAL,
                        ID
                    )
                    VALUES(
                        (
                            SELECT COALESCE(MAX(IDCAMPANHA), 0) FROM MSCUPONAGEMCAMPANHA
                        ), 
                        {item},
                        (
                            SELECT COALESCE(MAX(ID), 0) + 1 FROM MSCUPONAGEMCAMPANHAFILIAL
                        )
                    )
                ''')
            messages.success(request, f"Campanha inserida com sucesso")  
            
        
        elif 'edit' in request.POST:
            print(f'''
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
                    ENVIAEMAIL='{usaemail}',
                    TIPOINTENSIFICADOR='{tipointensificador}',
                    FORNECVALOR={fornecvalor},
                    PRODVALOR={prodvalor},
                    MARCAVALOR={marcavalor},
                    USAMARCA='{usamarca}',
                    RESTRINGE_FORNEC='{restringe_fornec}',
                    RESTRINGE_MARCA='{restringe_marca}',
                    RESTRINGE_PROD='{restringe_prod}'
                WHERE IDCAMPANHA = {codigo} 
            ''')
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
                    ENVIAEMAIL='{usaemail}',
                    TIPOINTENSIFICADOR='{tipointensificador}',
                    FORNECVALOR={fornecvalor},
                    PRODVALOR={prodvalor},
                    MARCAVALOR={marcavalor},
                    USAMARCA='{usamarca}',
                    RESTRINGE_FORNEC='{restringe_fornec}',
                    RESTRINGE_MARCA='{restringe_marca}',
                    RESTRINGE_PROD='{restringe_prod}',
                    ACUMULATIVO = '{acumulativo}'
                WHERE IDCAMPANHA = {codigo} 
            ''')
            
            cursor.execute(f'''
                DELETE FROM MSCUPONAGEMCAMPANHAFILIAL
                WHERE IDCAMPANHA = {codigo}
            ''')
            for item in filial:
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMCAMPANHAFILIAL
                    (
                        IDCAMPANHA, 
                        CODFILIAL,
                        ID
                    )
                    VALUES
                    (
                        {codigo}, 
                        {item},
                        (
                            SELECT COALESCE(MAX(ID), 0) + 1 FROM MSCUPONAGEMCAMPANHAFILIAL
                        ) 
                    )
                ''')
            messages.success(request, f"Campanha {codigo} editada com sucesso")
    
    conexao.commit()
    getTable()
    return render(request, 'campanhas/campanha.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def oldprodutos(request):
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
            SELECT 
                MSCUPONAGEMPROD.IDCAMPANHA, 
                MSCUPONAGEMPROD.CODPROD, 
                MSCUPONAGEMPROD.DTMOV, 
                PCPRODUT.DESCRICAO
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
                    nomeprod=exist[1]  # Supondo que `descricao` seja o nome do produto
                )
                messages.success(request, f"Produto {exist[1]} inserido com sucesso na campanha {idcampanha}")
            else:
                messages.error(request, f"Produto {exist[1]} já cadastrado na campanha {idcampanha}")
        
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
                                nomeprod=exist[1]
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

@login_required(login_url="/accounts/login/")
@staff_required
def oldfornecedores(request):
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
                    return render(request, 'fornecedores/fornecedores.html', context)
                    
                cursor.execute(f'''
                    SELECT CODFORNEC
                    FROM PCFORNEC
                    WHERE CODFORNEC = {codfornec}
                ''')
                exist_prod = cursor.fetchone()
                
                if exist_prod is None:
                    getTable()
                    messages.error(request, f"Não existe fornecedor cadastrado no winthor com codfornec {codfornec}, verifique a planilha")
                    return render(request, 'fornecedores/fornecedores.html', context)
                
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
                    return render(request, 'fornecedores/fornecedores.html', context)   
            
            messages.success(request, f"Todos os fornecedores foram inseridos com sucesso!")    
        conexao.commit()
    getTable()
    return render(request, 'fornecedores/fornecedores.html', context)

@login_required(login_url="/accounts/login/")
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
                    nomefornec=exist[1]
                )
                messages.success(request, f"Fornecedor {exist[0]} - {exist[1]} inserido com sucesso na campanha {exist_test[0]} - {exist_test[1]}")
            else:
                messages.error(request, f"Fornecedor {exist[0]} - {exist[1]} já cadastrado na campanha {exist_test[0]} - {exist_test[1]}")
        
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
                                nomefornec=exist[1]
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
            'id', 'IDCAMPANHA', 'CODCLI', 'NOMECLI', 'EMAIL', 'CPFCNPJ', 'DTMOV'
        )

    if request.method == 'POST':
        idcampanha = request.POST.get('IDCAMPANHA')
        codcli = request.POST.get('CODCLI')
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
                return render(request, 'sorteio/listanegra.html', context)
            
            if exist_cli is None:
                getTable()
                messages.error(request, f"Não existe cliente cadastrado com codcli {codcli}")
                return render(request, 'sorteio/listanegra.html', context)
            
            if not BlackList.objects.filter(IDCAMPANHA=idcampanha, CODCLI=codcli).exists():
                BlackList.objects.create(
                    IDCAMPANHA=idcampanha, 
                    CODCLI = exist_cli[0], 
                    EMAIL = exist_cli[2],
                    CPFCNPJ = exist_cli[3],
                    NOMECLI = exist_cli[1]
                )
                messages.success(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} inserido com sucesso na blacklist da campanha {idcampanha}")
            else:
                messages.error(request, f"Cliente {exist_cli[0]} - {exist_cli[1]} já cadastrado na blacklist da campanha {idcampanha}") 
            
        elif 'insertp' in request.POST:
            file = request.FILES.get("planilhas")
            if file:
                df = upload_planilha(file)
                if not isinstance(df, pd.DataFrame):
                    getTable()
                    messages.error(request, df)
                    return render(request, 'sorteio/listanegra.html', context)
            else:
                getTable()
                messages.error(request, "Nenhuma planilha enviada")
                return render(request, 'sorteio/listanegra.html', context)
            
            if not 'idcampanha' in df.columns or not 'codcli' in df.columns:
                getTable()
                messages.error(request, "Planilha enviada no formato errado")
                return render(request, 'sorteio/listanegra.html', context)

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        idcampanha = row['idcampanha']
                        codcli = row['codcli']

                        exist_cli = exist_client(cursor, codcli)
                        exist_test = exist_campanha(cursor, idcampanha)
                        
                        if exist_cli is None:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Não existe cliente cadastrado com codcli {codcli}")
                            return render(request, 'sorteio/listanegra.html', context)
            
                        if exist_test is None:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Não existe campanha cadastrada com idcampanha {idcampanha}")
                            return render(request, 'sorteio/listanegra.html', context)
            
                        if not BlackList.objects.filter(IDCAMPANHA=idcampanha, CODCLI=codcli).exists():
                            BlackList.objects.create(
                                IDCAMPANHA=idcampanha, 
                                CODCLI = exist_cli[0], 
                                EMAIL = exist_cli[2],
                                CPFCNPJ = exist_cli[3],
                                NOMECLI = exist_cli[1]
                            )
                        else:
                            transaction.rollback() 
                            getTable()
                            messages.error(request, f"Cliente {codcli} já cadastrado na campanha {idcampanha}, verifique a planilha")
                            return render(request, 'sorteio/listanegra.html', context)

                    messages.success(request, "Todos os clientes foram inseridos com sucesso!")

            except Exception as e:
                transaction.rollback()  # Garante que qualquer erro fará o rollback da transação
                getTable()
                messages.error(request, f"Ocorreu um erro ao processar a planilha: {str(e)}")
                return render(request, 'sorteio/listanegra.html', context)

        else:
            getTable()
            messages.error(request, "Ação não reconhecida")
            return render(request, 'sorteio/listanegra.html', context)

    getTable()
    return render(request, 'sorteio/listanegra.html', context)

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
                    nomemarca = exist[1]
                )
                messages.success(request, f"Marca {exist[0]} - {exist[1]} inserida com sucesso na campanha {exist_test[0]} - {exist_test[1]}")
            else:
                messages.error(request, f"Marca {exist[0]} - {exist[1]} já cadastrada na campanha {exist_test[0]} - {exist_test[1]}") 
            
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
                                nomemarca = exist[1]
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
                PCCLIENT.CODCLI > 0 AND 
                ATIVO = 'S'
            GROUP BY 
                PCCLIENT.CODCLI, 
                MSCUPONAGEM.IDCAMPANHA, 
                PCCLIENT.CODCLI, 
                PCCLIENT.CLIENTE
        ''')
        context['listaclients'] = cursor.fetchall()
        conexao.close()
    
    if request.method == 'POST':
        idcampanha = request.POST.get('idcampanha')
        codcli = request.POST.get('codcli')
        nomecli = request.POST.get('nomecli')
        if 'delete' in request.POST:
            cursor.execute(f'''
                UPDATE MSCUPONAGEM SET ATIVO = 'N', DTMOV = SYSDATE 
                WHERE 
                    IDCAMPANHA = {idcampanha} AND 
                    CODCLI = {codcli}
            ''')
            conexao.commit()
            messages.success(request,f'Cliente {codcli} - {nomecli} deletado com sucesso da campanha {idcampanha}')

    getTable()
    return render(request, 'campanhas/campanhaNumeros.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
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
                PCPEDC.NUMPED,
                MSCUPONAGEM.VALOR,
                COUNT(MSCUPONAGEM.NUMSORTE),
                TO_CHAR(PCPEDC."DATA", 'dd/mm/yyyy')
                
            FROM MSCUPONAGEM 
                INNER JOIN PCCLIENT ON PCCLIENT.CODCLI = MSCUPONAGEM.CODCLI
                LEFT JOIN PCPEDC ON MSCUPONAGEM.NUMPED = PCPEDC.NUMPED
            WHERE 
                MSCUPONAGEM.IDCAMPANHA = {idcampanha} AND 
                MSCUPONAGEM.NUMSORTE > 0 AND 
                PCCLIENT.CODCLI = {idclient}
            GROUP BY 
                MSCUPONAGEM.IDCAMPANHA, 
                PCCLIENT.CODCLI, 
                PCCLIENT.CLIENTE,
                PCPEDC.NUMPED,
                MSCUPONAGEM.VALOR,
                TO_CHAR(PCPEDC."DATA", 'dd/mm/yyyy')
        ''')
        context['listanumeros'] = cursor.fetchall()

    getTable()
    return render(request, 'campanhas/campanhaNumerosClient.html', context)

@login_required(login_url="/accounts/login/")
@staff_required
def campanhasidclientnumped(request, idcampanha, idclient, numped):
    context = {}
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    context['title'] = f'Lista de produtos no pedido {numped} do cliente {idclient}'
    context['numped'] = numped
    
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
        WHERE 
            IDCAMPANHA = {idcampanha} AND 
            DTEXCLUSAO IS NOT NULL
    ''')
    exist_delete = cursor.fetchone()
    if exist_delete:
        messages.error(request, f'Campanha {idcampanha} FOI EXCLUÍDA')
    
    cursor.execute(f'''
        SELECT IDCAMPANHA, CODCLI
        FROM MSCUPONAGEM
        WHERE 
            IDCAMPANHA = {idcampanha} AND 
            CODCLI = {idclient}
    ''')
    exist_client = cursor.fetchone()
    
    if exist_client is None:
        messages.error(request, f'Não existe nenhum cupom registrado para o cliente {idclient} na campanha {idcampanha}')
        return redirect(f'/campanhas/{idcampanha}/')
    
    cursor.execute(f'''
        SELECT IDCAMPANHA, CODCLI
        FROM MSCUPONAGEM
        WHERE 
            IDCAMPANHA = {idcampanha} AND 
            CODCLI = {idclient} AND 
            NUMPED = {numped}
    ''')
    exist_client = cursor.fetchone()
    
    if exist_client is None:
        messages.error(request, f'Não existe nenhuma venda registrada para o cliente {idclient} na campanha {idcampanha} com o numped ')
        return redirect(f'/campanhas/{idcampanha}/{idclient}/')
    
    context['campanha'] = f'{exist_active[1]}'
    context['cliente'] = f'{idclient}'
    
    def getTable():
        cursor.execute(f'''                
            SELECT 
                PCMOV.CODPROD, 
                PCPRODUT.CODAUXILIAR,
                PCMOV.CODFILIAL, 
                PCPRODUT.DESCRICAO, 
                PCMOV.PUNIT,
                PCMOV.QT,
                PCPRODUT.CODFORNEC,
                PCFORNEC.FORNECEDOR
            FROM PCMOV 
                INNER JOIN PCPRODUT ON (PCPRODUT.CODPROD = PCMOV.CODPROD)
                INNER JOIN PCFORNEC ON (pcprodut.codfornec = PCFORNEC.codfornec)
            WHERE NUMPED = {numped}
        ''')
        context['dados'] = cursor.fetchall()

    getTable()
    return render(request, 'campanhas/campanhaItems.html', context)

def cadastro_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Substitua com a URL para uma página de sucesso ou outra ação desejada
    else:
        form = ClienteForm()
    return render(request, 'clientes/cadastro.html', {'form': form})

@login_required(login_url="/accounts/login/")
@staff_required
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
                WHERE 
                    MSCUPONAGEM.IDCAMPANHA = {idcampanha}
                    AND MSCUPONAGEM.NUMSORTE > 0
                    AND PCCLIENT.CODCLI > 0
                    AND MSCUPONAGEM.ATIVO = 'S'
                    AND not exists (
                        SELECT CODCLI FROM MSCUPONAGEMVENCEDORES 
                        WHERE NUMSORTE = MSCUPONAGEM.NUMSORTE
                    )
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
        
        if numsorte:
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
@staff_required
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
@staff_required
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

