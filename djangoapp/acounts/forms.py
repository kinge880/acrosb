from django import forms
from .models import PresentationSettings
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from .models import Cliente
import re

class ClienteForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'required': True, 
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 
                'classdiv': 'col-12 col-md-6 mb-3', 
                'autocomplete': 'off'
            }),
        label="Confirmar Senha"
    )

    class Meta:
        model = Cliente
        fields = [
            'nome', 'tipo_pessoa', 'cnpf_cnpj', 'telefone', 'email', 'cep', 'cidade',
            'estado', 'bairro', 'rua', 'numero', 'data_nascimento', 'genero', 'senha', 
            'ibge', 'confirmar_senha', 'aceita_comunicacao', 'concordo_regulamento'
        ]
        
        TIPO_PESSOA_CHOICES = [
            ('F', 'Física'),
            ('J', 'Jurídica'),
        ]
        widgets = widgets = {
            'nome': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 mb-3',
                'autocomplete': 'off',
                'maxlength': '60'
            }),
            'tipo_pessoa': forms.Select(attrs={'required': True, 'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off' }),
            'cnpf_cnpj': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '18'
            }),
            'telefone': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '13'
            }),
            'email': forms.EmailInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '100'
            }),
            'cep': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '9'
            }),
            'cidade': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '15'
            }),
            'estado': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '2'
            }),
            'bairro': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '40'
            }),
            'rua': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '40'
            }),
            'numero': forms.TextInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '6'
            }),
            'genero': forms.Select(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'type': 'date',
                'classdiv': 'col-12 col-md-6 mb-3',
                'classlabel': 'user-label-date-cosmic-cascade-tetra-49m7',
                'autocomplete': 'off'
            }),
            'senha': forms.PasswordInput(attrs={
                'required': True,
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-md-6 mb-3',
                'autocomplete': 'off',
                'maxlength': '100'
            }),
            'ibge': forms.HiddenInput(attrs={
                'class': 'form-control d-none col-12',
                'classdiv': 'd-none'
            }),
            'aceita_comunicacao': forms.CheckboxInput(attrs={
                'class': 'form-check-input col-12',
                'classdiv': 'form-check form-switch col-12 mb-3 ms-2',
                'autocomplete': 'off'
            }),
            'concordo_regulamento': forms.CheckboxInput(attrs={
                'required': True,
                'class': 'form-check-input col-12',
                'classdiv': 'form-check form-switch col-12 mb-3 ms-2',
                'autocomplete': 'off'
            })
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].label = 'Digite seu nome completo'
        self.fields['tipo_pessoa'].label = 'Tipo de Pessoa'
        
        choices = list(self.fields['tipo_pessoa'].choices)
        choices = [choice for choice in choices if choice[0] != '']
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
        self.fields['genero'].choices = choices
        
        self.fields['senha'].label = 'Senha'
        self.fields['confirmar_senha'].label = 'Confirmar Senha'
        self.fields['ibge'].label = ''
        self.fields['aceita_comunicacao'].label = 'Aceito receber comunicações do clube de ofertas'
        self.fields['concordo_regulamento'].label = 'Afirmo que todos os dados acima são verdadeiros e concordo com as <a href="/accounts/politicas/privacidade/">políticas de privacidade</a>'
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '')
        return nome[:40]  # Trunca se exceder 60 caracteres

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '')
        return telefone[:13]  # Trunca para 13 caracteres

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        email = email[:100]  # Trunca para 100 caracteres
        if Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_cidade(self):
        cidade = self.cleaned_data.get('cidade', '')
        return cidade[:15]  # Trunca para 15 caracteres

    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '')
        return estado[:2]  # Trunca para 2 caracteres

    def clean_bairro(self):
        bairro = self.cleaned_data.get('bairro', '')
        return bairro[:40]  # Trunca para 40 caracteres

    def clean_rua(self):
        rua = self.cleaned_data.get('rua', '')
        return rua[:40]  # Trunca para 40 caracteres

    def clean_numero(self):
        numero = self.cleaned_data.get('numero', '')
        return numero[:6]  # Trunca para 6 caracteres

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')
        return cep[:9]  # Trunca para 9 caracteres
    
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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_cnpf_cnpj(self):
        cnpf_cnpj = self.cleaned_data.get('cnpf_cnpj')
        if Cliente.objects.filter(cnpf_cnpj=cnpf_cnpj).exists():
            raise forms.ValidationError("Este CPF/CNPJ já está cadastrado.")
        return cnpf_cnpj

class PresentationSettingsForm(forms.ModelForm):
    class Meta:
        model = PresentationSettings
        fields = [
            'idempresa',
            'background_type',
            'background_color', 
            'background_url', 
            'filter_color', 
            'background_type_mobile',
            'background_color_mobile', 
            'background_url_mobile', 
            'filter_color_mobile', 
            'initial_text', 
            'logo_type', 
            'logo_text', 
            'logo_image',
            'logo_type_mobile', 
            'logo_text_mobile', 
            'logo_image_mobile',
            'error_message_suport'
        ]
