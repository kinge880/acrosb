from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
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
from django.core.serializers import serialize
from django.db.models import OuterRef, Subquery
from django.contrib.postgres.aggregates import ArrayAgg
from project.conexao_postgresql import *
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
    context['tableOnlyView'] = 'SIM'
    
    if request.method == 'POST':
        context['postmethod'] = True
        currenttime = datetime.now()
        context['currenttime'] = currenttime
        context['parametroValor'] = '100'
        cpf = request.POST.get('cpf')
        email = request.POST.get('email').strip()
        
        # Limpando o CPF para remover caracteres não numéricos
        cpf_cleaned = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se o CPF e email estão na base de clientes (simulação de PCCLIENT via ORM)
        cpf_exist = Cuponagem.objects.filter(
            cpf_cnpj=cpf_cleaned, 
            emailcli__iexact=email
        ).values('codcli', 'nomecli', 'emailcli').first()

        if cpf_exist is None:
            messages.error(request, "O CPF/CNPJ ou email informados não foram encontrados")
            context['postmethod'] = False
            return render(request, 'pesquisacpf.html', context)

        # Busca por campanhas ativas
        campanha_ativa = Campanha.objects.filter(ativo='S').values('idcampanha').first()

        if campanha_ativa is None:
            messages.warning(request, "Atualmente não existe nenhuma campanha promocional ativa no sistema")
            context['postmethod'] = False
            return render(request, 'pesquisacpf.html', context)

        # Buscando cupons do cliente na campanha ativa
        num_da_sorte = Cuponagem.objects.filter(
            codcli=cpf_exist['codcli'],
            idcampanha=campanha_ativa['idcampanha']
        ).values('numsorte', 'idcampanha__descricao', 'idcampanha__valor', 'dataped')

        context['num_da_sorte'] = num_da_sorte
        context['cpf_exist'] = cpf_exist
            
    return render(request, 'pesquisacpf.html', context)

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
        form = MscuponagemCampanhaForm(request.POST)
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
            if not Campanha.objects.filter(ativo='S').exists():
                campanha = get_object_or_404(Campanha, pk=idcampanha)
                campanha.ativo = 'S'
                campanha.save()
                messages.success(request, f"Campanha {campanha.idcampanha} - {campanha.descricao} ativada com sucesso")
            else:
                messages.error(request, "Já existe uma campanha ativa, somente uma pode estar ativa por vez.")
        
        elif 'insert' in request.POST:
            if form.is_valid():
                nova_campanha = form.save(commit=False)
                nova_campanha.ativo = 'S' if not Campanha.objects.filter(ativo='S').exists() else 'N'
                nova_campanha.dtultalt = timezone.now()
                nova_campanha.save()
                
                messages.success(request, "Campanha inserida com sucesso")
            else:
                messages.error(request, "Erro ao inserir campanha") 
            
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
                messages.error(request, "Erro ao editar campanha")

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
                    NOMECLI = exist_cli[1],
                    DTMOV = datetime.now()
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
                                NOMECLI = exist_cli[1],
                                DTMOV = datetime.now()
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
                    nomemarca = exist[1],
                    dtmov = datetime.now()
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
    
    context['campanha'] = campanha.descricao
    
    def getTable():
        # Consulta usando ORM do Django
        dados = Cuponagem.objects.filter(
            idcampanha=campanha, 
            ativo='S'
        ).values('idcampanha', 'codcli', 'nomecli').annotate(total_numsorte=Count('numsorte'))
        
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

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cuponagem, Campanha

@login_required(login_url="/accounts/login/")
@staff_required
def campanhasidclient(request, idcampanha, idclient):
    context = {}
    context['title'] = f'Lista de números da sorte do cliente {idclient}'
    context['tituloDelete'] = 'Deletar número da sorte'
    context['primarykey'] = 'id'
    context['appname'] = 'cpfcli'
    context['modelname'] = 'Cuponagem'
    context['nomecolum'] = 'numsorte'
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
    
    context['campanha'] = campanha.descricao
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
def campanhasidclientnumped(request, idcampanha, idclient, numped):
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
    
    context['campanha'] = f'{campanha.descricao}'
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
            count_cupons=models.Count('cuponagem')
        )

        today = now().date()  # Data atual
        processed_campaigns = []
        
        for campanha in campaigns:
            if campanha.dtfim and campanha.dtfim <= datetime.today().date() and campanha.count_cupons and campanha.count_cupons > 0:
                # O dia atual é superior à data de término da campanha
                permite_sorteio = 'S'
            else:
                # A campanha ainda está ativa
                permite_sorteio = 'N'
            
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
                'permite_sorteio': permite_sorteio
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

