from django import forms
from .models import Cliente
import re

from django import forms
from .models import Cliente
import re

class ClienteForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}),
        label="Confirmar Senha"
    )

    class Meta:
        model = Cliente
        fields = [
            'nome', 'tipo_pessoa', 'cpf', 'telefone', 'email', 'endereco', 'cidade',
            'estado', 'cep', 'data_nascimento', 'genero', 'senha'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'}),
            'tipo_pessoa': forms.Select(attrs={'class': 'form-select'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu CPF ou CNPJ'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu número celular'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu e-mail'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu endereço completo'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua cidade'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu CEP'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'senha': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
        }

    def clean_cpf(self):
        cpf_cnpj = self.cleaned_data.get('cpf')
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
        # CPF validation logic (you can use a library or write your own validation)
        if len(cpf) != 11:
            return False
        # Implement the validation algorithm or use a library here
        return True

    def validar_cnpj(self, cnpj):
        # CNPJ validation logic (you can use a library or write your own validation)
        if len(cnpj) != 14:
            return False
        # Implement the validation algorithm or use a library here
        return True

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha != confirmar_senha:
            self.add_error('confirmar_senha', 'Senhas não conferem.')