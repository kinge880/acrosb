from django import forms
import re
from .models import *
from reusable.views import *
from django.forms import inlineformset_factory

class ClienteForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'required': True, 
                'class': 'input-cosmic-cascade-tetra-49m7 col-12', 
                'classdiv': 'col-12 col-md-6 mb-3', 
                'autocomplete': 'off'
            }),
        label="Confirmar Senha"
    )

    class Meta:
        model = Cliente
        fields = [
            'nome', 'tipo_pessoa', 'cnpf_cnpj', 'telefone', 'email', 'cep', 'cidade',
            'estado', 'bairro', 'rua', 'numero', 'data_nascimento', 'genero', 'senha'
        ]
        
        TIPO_PESSOA_CHOICES = [
            ('F', 'Física'),
            ('J', 'Jurídica'),
        ]
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'required': True, 
                    'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 
                    'classdiv': 'col-12 mb-3', 
                    'autocomplete': 'off'
                }),
            'tipo_pessoa': forms.Select(
                attrs={
                    'required': True, 
                    'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 
                    'classdiv': 'col-12 col-md-6 mb-3', 
                    'autocomplete': 'off'
                }),
            'cnpf_cnpj': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'telefone': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 mb-3', 'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 mb-3', 'autocomplete': 'off'}),
            'cep': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'cidade': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'estado': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'bairro': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'rua': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'numero': forms.TextInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'genero': forms.Select(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'data_nascimento': forms.DateInput(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'type': 'date', 'classdiv': 'col-12 col-md-6 mb-3', 'classlabel': 'user-label-date-cosmic-cascade-tetra-49m7', 'autocomplete': 'off'}),
            'senha': forms.PasswordInput(
                attrs={
                    'required': True, 
                    'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 
                    'classdiv': 'col-12 col-md-6 mb-3',
                    'autocomplete': 'off'
                }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = 'Digite seu nome completo'
        self.fields['tipo_pessoa'].label = 'Tipo de Pessoa'
        
        choices = list(self.fields['tipo_pessoa'].choices)
        choices = [choice for choice in choices if choice[0] != '']
        choices.insert(0, ('', ' '))
        self.fields['tipo_pessoa'].choices = choices
        
        self.fields['cnpf_cnpj'].label = 'Cpf/Cnpj'
        self.fields['telefone'].label = 'Número de Telefone'
        self.fields['email'].label = 'Endereço de E-mail'
        self.fields['cidade'].label = 'Cidade'
        self.fields['estado'].label = 'Estado'
        self.fields['bairro'].label = 'Bairro'
        self.fields['rua'].label = 'Rua'
        self.fields['numero'].label = 'Número'
        self.fields['cep'].label = 'CEP'
        self.fields['data_nascimento'].label = 'Data de Nascimento'
        self.fields['genero'].label = 'Gênero'
        
        choices = list(self.fields['genero'].choices)
        choices = [choice for choice in choices if choice[0] != '']
        choices.insert(0, ('', ' '))
        self.fields['genero'].choices = choices
        
        self.fields['senha'].label = 'Senha'
        self.fields['confirmar_senha'].label = 'Confirmar Senha'
    
    def clean_cnpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cnpf_cnpj')
        tipo_pessoa = self.cleaned_data.get('tipo_pessoa')

        # Remove non-numeric characters
        cpf_cnpj = re.sub(r'\D', '', cpf_cnpj)

        if tipo_pessoa == 'F':
            if not self.validar_cpf(cpf_cnpj):
                raise forms.ValidationError('CPF inválido.')
        elif tipo_pessoa == 'J':
            if not self.validar_cnpj(cpf_cnpj):
                raise forms.ValidationError('CNPJ inválido.')
        else:
            raise forms.ValidationError('Tipo de pessoa inválido.')

        return cpf_cnpj

    def validar_cpf(self, cpf):
        # Implement CPF validation logic here
        if len(cpf) != 11:
            return False
        # Add actual CPF validation algorithm here
        return True

    def validar_cnpj(self, cnpj):
        # Implement CNPJ validation logic here
        if len(cnpj) != 14:
            return False
        # Add actual CNPJ validation algorithm here
        return True

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha != confirmar_senha:
            self.add_error('confirmar_senha', 'Senhas não conferem.')

class MscuponagemCampanhaForm(forms.ModelForm):
    filial = forms.MultipleChoiceField(
        choices=obter_choices_filiais(),
        required=True,
        label='Lista de filiais',
        widget=forms.SelectMultiple(attrs={'class': ' select2', 'classdiv': 'col-12  mb-3', 'autocomplete': 'off', 'select2Label': 'select'})
    )
    class Meta:
        model = MscuponagemCampanha
        fields = [
            'idcampanha',  'descricao', 'filial', 'dtinit', 'dtfim', 'enviaemail', 'acumulativo', 'valor', 
            'restringe_fornec', 'restringe_marca', 'restringe_prod',
            'tipointensificador', 'multiplicador', 'usafornec',  'fornecvalor', 'usamarca', 'marcavalor', 'usaprod', 'prodvalor'
        ]
        widgets = {
            'idcampanha': forms.HiddenInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'descricao': forms.TextInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 mb-3', 'autocomplete': 'off'}),
            'dtinit': forms.DateInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'type': 'date', 'classdiv': 'col-12 col-md-4 mb-3', 'classlabel': 'user-label-date-cosmic-cascade-tetra-49m7', 'autocomplete': 'off'}),
            'dtfim': forms.DateInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'type': 'date', 'classdiv': 'col-12 col-md-4 mb-3', 'classlabel': 'user-label-date-cosmic-cascade-tetra-49m7', 'autocomplete': 'off'}),
            'enviaemail': forms.Select(choices=[
                ('N', '1 - Não enviar email'),
                ('S', '2 - Enviar email ao cliente informando os números da sorte obtidos')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off'}),
            'acumulativo': forms.Select(choices=[
                ('N', '1 - Não acumular saldo entre vendas'),
                ('S', '2 - Somente acumular saldo entre vendas com o valor total superior ao número da sorte'),
                ('T', '3 - Acumular saldo entre todas as vendas')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-8 mb-3', 'autocomplete': 'off'}),
            'valor': forms.NumberInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off', 'min': '1'}),
            'restringe_fornec': forms.Select(choices=[
                ('N', '1 - Não utilizar restrição por fornecedor'),
                ('C', '2 - Restrição por fornecedor cadastrado'),
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off'}),
            'restringe_marca': forms.Select(choices=[
                ('N', '1 - Não utilizar restrição por marca'),
                ('C', '2 - Restrição por marca cadastrada'),
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off'}),
            'restringe_prod': forms.Select(choices=[
                ('N', '1 - Não utilizar restrição por produto'),
                ('C', '2 - Restrição por produto cadastrado'),
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off'}),
            'tipointensificador': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador'),
                ('M', '2 - Multiplicação'),
                ('S', '3 - Soma')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-8 mb-3', 'autocomplete': 'off'}),
            'multiplicador': forms.NumberInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off', 'min': '1'}),
            'usamarca': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador por marca'),
                ('C', '2 - Intensificador por marca cadastrada'),
                ('M', '3 - Intensificador por marca multipla')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-8 mb-3', 'autocomplete': 'off'}),
            'marcavalor': forms.NumberInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off', 'min': '1'}),
            'usafornec': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador por fornecedor'),
                ('C', '2 - Intensificador por fornecedor cadastrado'),
                ('M', '3 - Intensificador por fornecedor multiplo')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-8 mb-3', 'autocomplete': 'off'}),
            'fornecvalor': forms.NumberInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off', 'min': '1'}),
            'usaprod': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador por produto'),
                ('C', '2 - Utilizar intensificador por produto cadastrado'),
                ('M', '3 - Utilizar intensificador por produto multiplo')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-8 mb-3', 'autocomplete': 'off'}),
            'prodvalor': forms.NumberInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-4 mb-3', 'autocomplete': 'off', 'min': '1'}),
        }
        
        labels = {
            'idcampanha': 'Código interno',
            'descricao': 'Descrição da campanha',
            'dtinit': 'Data inicial',
            'dtfim': 'Data final',
            'enviaemail': 'Envia email',
            'valor': 'Valor por número',
            'acumulativo': 'Acumulação de saldo entre vendas',
            'restringe_fornec': 'Restrição por fornecedor', 
            'restringe_marca': 'Restrição por marca', 
            'restringe_prod': 'Restrição por produto',
            'tipointensificador': 'Tipo de intensificador utilizado',
            'usafornec': 'Utiliza intensificador por fornecedor',
            'usamarca': 'Utiliza intensificador por marca',
            'usaprod': 'Utiliza intensificador por produto',
            'multiplicador': 'Valor do intensificador',
            'fornecvalor': 'Valor do fornecedor',
            'marcavalor': 'Valor da marca',
            'prodvalor': 'Valor de produtos',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        # Primeiro, salve o registro da campanha como antes
        campanha = super().save(commit)

        # Obtenha as filiais selecionadas
        codfiliais = self.cleaned_data.get('filial')

        if codfiliais:
            # Crie registros de CuponagemCampanhaFilial para cada filial selecionada
            CuponagemCampanhaFilial.objects.bulk_create(
                CuponagemCampanhaFilial(idcampanha=campanha, codfilial=codfilial)
                for codfilial in codfiliais
            )

        return campanha
    
class MarcasForm(forms.ModelForm):
    class Meta:
        model = Marcas
        fields = [
            'idcampanha', 'codmarca', 'nomemarca'
        ]
        widgets = {
            'idcampanha': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'codmarca': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'nomemarca': forms.HiddenInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12 d-none',
                'classdiv': 'd-none'
            })
        }
        
        labels = {
            'idcampanha': 'Código da Campanha',
            'codmarca': 'Código da Marca'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize widgets or other fields if needed
        

class BlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = [
            'IDCAMPANHA', 'CODCLI'
        ]
        widgets = {
            'IDCAMPANHA': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'CODCLI': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            })
        }
        
        labels = {
            'IDCAMPANHA': 'Código da Campanha',
            'CODCLI': 'Código do Cliente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalize widgets ou outros campos se necessário