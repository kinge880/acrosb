from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth import login as loginDjango
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings
from django.db.models import Q
from project.conexao_postgresql import *
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from functools import wraps
from django.contrib import messages
from .forms import *
from django.db import transaction
from .models import *
from project.conexao_postgresql import *
from project.oracle import *
from reusable.views import *

#Anonymous required 
def anonymous_required(function=None, redirect_url='/'):

    if not redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator

def logout_view(request):
    logout(request)

    return redirect('/')

#controles de login e cadastro de usuário
@anonymous_required
def login(request):
    
    if request.method == 'POST' :
        usuario = request.POST.get("username")
        senha = request.POST.get("password")
        
        user = authenticate(username=usuario, password=senha)

        if user:
            loginDjango(request, user)
            return redirect('/')
        else:
            messages.error(request, f'Nome de usuário ou senha incorretos!')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html', {'login': 'login'})

@transaction.atomic
def cadastro_cliente(request):
    
    if request.method == 'POST':
        print(request.POST)
        form = ClienteForm(request.POST)
        
        # Validações básicas
        if not form.is_valid():
            return render(request, 'clientes/cadastro.html', {'form': form})
        
        try:
            cliente = form.save(commit=False)
                
            # Criação do usuário Django
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Usando e-mail como username
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['nome'].split()[0],  # Primeiro nome
                last_name=" ".join(form.cleaned_data['nome'].split()[1:])  # Último nome ou sobrenomes
            )
            
            # Configura a senha com hash (segurança)
            user.set_password(form.cleaned_data['senha'])  # Senha com hash seguro
            
            empress = empresa.objects.first()
            
            #valido no winthor se existe
            conexao = conexao_oracle()
            cursor = conexao.cursor()
            
            client_winthor = exist_client_cpf_email(cursor, form.cleaned_data['email'], form.cleaned_data['cnpf_cnpj'])
            
            if client_winthor and client_winthor[0]:
                cliente.codcli = client_winthor[0]
            else:
                codcli_winthor = obter_cod_client(cursor, form.cleaned_data['email'], form.cleaned_data['cnpf_cnpj'], conexao)
                if cliente.tipo_pessoa == 'F':
                    ieent = 'ISENTO'
                    codativ = 32
                    cliente.codativ = 32
                    cliente.ieent = 'ISENTO'
                else:
                    ieent = 'ISENTO'
                    codativ = 32
                    cliente.codativ = 32
                    cliente.ieent = 'ISENTO'
                    """ ieent = form.cleaned_data['ieent']
                    cliente.ieent = form.cleaned_data['ieent']
                    codativ = form.cleaned_data['codativ']
                    cliente.codativ = form.cleaned_data['codativ'] """
                
                praca = obter_praca(cursor, cliente.cidade)
                if praca:
                    codpraca = praca[0]
                else:
                    codpraca = '1'
                
                cursor.execute(f'''
                    INSERT INTO PCCLIENT (
                        CODCLI,         -- Código do cliente (substitua por um valor único para o teste)
                        CLIENTE,        -- Razão social do cliente
                        ENDERCOB,       -- Endereço de cobrança
                        NUMEROCOB,      -- Número do endereço de cobrança
                        BAIRROCOB,      -- Bairro de cobrança
                        TELCOB,         -- Telefone de cobrança
                        MUNICCOB,       -- Município de cobrança
                        ESTCOB,         -- UF de cobrança
                        CEPCOB,         -- Cep de cobrança
                        ENDERENT,       -- Endereço comercial
                        NUMEROENT,      -- Número do endereço de entrega
                        BAIRROENT,      -- Bairro de entrega
                        TELENT,         -- Telefone de entrega
                        MUNICENT,       -- Município de entrega
                        ESTENT,         -- UF de entrega
                        CEPENT,         -- Cep de entrega
                        CGCENT,         -- CGC ou CPF do cliente
                        IEENT,          -- Inscrição estadual
                        DTULTCOMP,      -- Data da última compra
                        CODATV1,        -- Código do ramo de atividade
                        BLOQUEIO,       -- Indica se cliente está bloqueado
                        CODUSUR1,       -- Código do vendedor que atende
                        CODUSUR2,       -- Código do segundo vendedor
                        FAXCLI,         -- Fax do cliente
                        LIMCRED,        -- Limite de crédito
                        OBS,            -- Motivo do bloqueio
                        DTPRIMCOMPRA,   -- Data da primeira compra
                        CODCOB,         -- Forma de pagamento
                        DTBLOQ,         -- Data do bloqueio
                        DTCADASTRO,     -- Data do cadastro
                        CODPRACA,       -- Código da praça
                        FANTASIA,       -- Nome fantasia do cliente
                        OBS2,           -- Observação adicional
                        PONTOREFER,     -- Ponto de referência
                        OBSCREDITO,     -- Observação sobre limite de crédito
                        TIPOFJ,         -- Tipo de pessoa
                        TELENT1,        -- Telefone adicional
                        EMAIL,          -- Email do cliente
                        CODPLPAG,       -- Código do prazo de pagamento
                        OBS3,           -- Observação adicional
                        OBS4,           -- Observação adicional
                        NUMSEQ,         -- Sequência de atendimento
                        OBSENTREGA1,    -- Observações sobre entrega
                        OBSENTREGA2,    -- Observações sobre entrega
                        OBSENTREGA3,    -- Observações sobre entrega
                        OBSGERENCIAL1,  -- Observação gerencial
                        OBSGERENCIAL2,  -- Observação gerencial
                        OBSGERENCIAL3,  -- Observação gerencial
                        OBSERVACAO,     -- Observações adicionais
                        OBS_ADIC,       -- Observações gerais
                        RG,             -- Documento de identidade
                        CODFILIALNF,    -- Filial de faturamento
                        EMITEDUP,       -- Emite duplicata mercantil
                        CODMUNICIPIO,   -- Código do município no IBGE
                        ENDERCOM,       -- Endereço de entrega
                        NUMEROCOM,      -- Número de entrega
                        BAIRROCOM,      -- Bairro de entrega
                        TELCOM,         -- Telefone comercial
                        MUNICCOM,       -- Município de entrega
                        ESTCOM,         -- UF de entrega
                        CEPCOM,         -- CEP de entrega
                        CONSUMIDORFINAL,-- Consumidor final
                        CONTRIBUINTE,   -- Contribuinte
                        CLIENTPROTESTO, -- Cliente passível de protesto
                        CLIATACADO -- cliente atacado
                    ) VALUES (
                        {codcli_winthor[0]}, -- CODCLI (substitua com um valor único)
                        '{cliente.nome}', -- CLIENTE
                        '{cliente.rua}', -- ENDERCOB
                        '{cliente.numero}', -- NUMEROCOB
                        '{cliente.bairro}', -- BAIRROCOB
                        '{cliente.telefone}', -- TELCOB
                        '{cliente.cidade}',    -- MUNICCOB
                        '{cliente.estado}', -- ESTCOB
                        '{cliente.cep}',     -- CEPCOB
                        '{cliente.rua}', -- ENDERENT
                        '{cliente.numero}',           -- NUMEROENT
                        '{cliente.bairro}',        -- BAIRROENT
                        '{cliente.telefone}',    -- TELENT
                        '{cliente.cidade}',    -- MUNICENT
                        '{cliente.estado}',            -- ESTENT
                        '{cliente.cep}',     -- CEPENT
                        '{cliente.cnpf_cnpj}', -- CGCENT
                        '{ieent}',     -- IEENT
                        TRUNC(SYSDATE), -- DTULTCOMP
                        {codativ},           -- CODATV1
                        'N',             -- BLOQUEIO
                        '1',             -- CODUSUR1
                        NULL,             -- CODUSUR2
                        NULL,    -- FAXCLI
                        0,  -- LIMCRED
                        NULL, -- OBS
                        TRUNC(SYSDATE), -- DTPRIMCOMPRA
                        'COBS', -- CODCOB
                        NULL, -- DTBLOQ (nulo se não bloqueado)
                        SYSDATE, -- DTCADASTRO
                        {codpraca},  -- CODPRACA
                        '{cliente.nome[:40]}',     -- FANTASIA
                        NULL, -- OBS2
                        NULL, -- PONTOREFER
                        NULL, -- OBSCREDITO
                        '{cliente.tipo_pessoa}',             -- TIPOFJ (F para física)
                        '{cliente.telefone}',    -- TELENT1
                        '{cliente.email}', -- EMAIL
                        '1',            -- CODPLPAG
                        NULL, -- OBS3
                        NULL, -- OBS4
                        NULL,           -- NUMSEQ
                        NULL, -- OBSENTREGA1
                        NULL, -- OBSENTREGA2
                        NULL, -- OBSENTREGA3
                        NULL,   -- OBSGERENCIAL1
                        NULL, -- OBSGERENCIAL2
                        NULL, -- OBSGERENCIAL3
                        'CADASTRADO PELO SYSP', -- OBSERVACAO
                        NULL, -- OBS_ADIC
                        NULL,     -- RG
                        NULL,            -- CODFILIALNF
                        'N',             -- EMITEDUP
                        {cliente.ibge},       -- CODMUNICIPIO (Rio Branco)
                        '{cliente.rua}', -- ENDERCOM
                        '{cliente.numero}',           -- NUMEROCOM
                        '{cliente.bairro}', -- BAIRROCOM
                        '{cliente.telefone}',    -- TELCOM
                        '{cliente.cidade}',    -- MUNICCOM
                        '{cliente.estado}',            -- ESTCOM
                        '{cliente.cep}',     -- CEPCOM
                        'S',             -- CONSUMIDORFINAL
                        'N',             -- CONTRIBUINTE
                        'S',-- CLIENTPROTESTO
                        'S' -- CLIATACADO
                    )
                ''')
                
                new_client_winthor= exist_client_cpf_email(cursor, form.cleaned_data['email'], form.cleaned_data['cnpf_cnpj'])
                
                cliente.codcli = new_client_winthor[0]
            
            user.save()
            cliente.save()  # Agora salvamos o cliente
            profile = Profile.objects.create(user=user, idempresa=empress, client = cliente)
            profile.save()
            conexao.commit()
                
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login') 

        except IntegrityError as e:
            # Se qualquer erro ocorrer durante a transação, faça rollback
            transaction.set_rollback(True)
            messages.error(request, f"Ocorreu um erro ao realizar o seu cadastro: {str(e)}")
        except Exception as e:
            # Mensagem genérica para outros erros
            transaction.set_rollback(True)
            messages.error(request, f"Ocorreu um erro inesperado: {str(e)}")
    else:
        form = ClienteForm()

    return render(request, 'clientes/cadastro.html', {'form': form})

@login_required(login_url="/accounts/login/")
def config_user_page(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        idempres = empresa.objects.get(id=profile.idempresa.id)
        
        dictform = request.POST.copy()
        dictform['idempresa'] = idempres
        
        form = PresentationSettingsForm(dictform, request.FILES, instance=PresentationSettings.objects.first())
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('userpagepanel')
        else:
            messages.error(request, 'Erro ao salvar configurações. Verifique os campos e tente novamente.')
            # Adiciona os erros de validação aos messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
    else:
        instance = PresentationSettings.objects.first() or PresentationSettings()
        form = PresentationSettingsForm(instance=instance)

    context = {
        'form': form
    }
    return render(request, 'config/user_panel.html', context)


def privacity(request):
    
    return render(request, 'privacity-template.html')