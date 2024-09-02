from django import forms
import re
from .models import Cliente

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
