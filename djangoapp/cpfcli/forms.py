from django import forms
from .models import *
from reusable.views import *
from reusable.models import *
from django.forms import inlineformset_factory


class MscuponagemCampanhaForm(forms.ModelForm):
    filial = forms.MultipleChoiceField(
        choices=obter_choices_filiais(),
        required=True,
        label='Lista de filiais',
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2', 'classdiv': 'col-12  mb-3', 'autocomplete': 'off', 'select2Label': 'select'})
    )
    class Meta:
        model = Campanha
        fields = [
            'idcampanha',  'descricao', 'filial', 'usa_numero_da_sorte', 'tipo_cluster_cliente', 'dtinit', 'dtfim', 'enviaemail', 'acumulativo', 'valor', 
            'restringe_fornec', 'restringe_marca', 'restringe_prod',
            'tipointensificador', 'multiplicador', 'usafornec',  'fornecvalor', 'usamarca', 'marcavalor', 'usaprod', 'prodvalor', 'acumula_intensificadores',
            'logo_campanha',
        ]
        widgets = {
            'idcampanha': forms.HiddenInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'descricao': forms.TextInput(attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 'classdiv': 'col-12 col-md-12 mb-3', 'autocomplete': 'off'}),
            'usa_numero_da_sorte': forms.Select(choices=[
                ('S', '1 - Deve utilizar números da sorte'),
                ('N', '2 - Deve utilizar cuponagem física no caixa')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
            'tipo_cluster_cliente': forms.Select(choices=[
                ('N', '1 - Não utiliza Cluster por cliente'),
                ('B', '2 - Deve utilizar BlackList'),
                ('W', '3 - Deve utilizar WhiteList')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),
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
            'acumula_intensificadores': forms.Select(choices=[
                ('N', '1 - Não acumular intensificadores'),
                ('A', '2 - Acumular intensificadores')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-8 mb-3', 'autocomplete': 'off'}),
            'logo_campanha': forms.FileInput(attrs={'class': 'form-control col-12', 'classdiv': 'col-12 col-md-6 mb-3', 'autocomplete': 'off'}),

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
            'tipo_cluster_cliente': 'Qual o tipo de cluster dos clientes',
            'acumula_intensificadores': 'Acumulação de intensificadores',
            'logo_campanha': 'Logo da campanha'
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
            CampanhaFilial.objects.bulk_create(
                CampanhaFilial(idcampanha=campanha.idcampanha, codfilial=codfilial)
                for codfilial in codfiliais
            )

        return campanha
    
class AgentForm(forms.Form):
    codfilial = forms.CharField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
            'classdiv': 'col-12 col-md-3 mb-3',
            'autocomplete': 'off'
        }),
        label='Código da Filial'
    )
    numcaixa = forms.CharField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
            'classdiv': 'col-12 col-md-2 mb-3',
            'autocomplete': 'off'
        }),
        label='Número do Caixa'
    )
    agent_ip = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
            'classdiv': 'col-12 col-md-2 mb-3',
            'autocomplete': 'off'
        }),
        label='IP do Agente'
    )
    status = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 
            'classdiv': 'col-12 col-md-3 mb-3',
            'autocomplete': 'off'
        }),
        choices=[
            ('', 'Todos'),
            ('Ativo', 'Ativo'),
            ('Desativado', 'Desativado'),
            ('Falha', 'Falha'),
        ],
        label='Status'
    )
        
class MarcasForm(forms.ModelForm):
    class Meta:
        model = Marcas
        fields = [
            'idcampanha', 'codmarca', 'tipo'
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
            'tipo': forms.Select(choices=[
                ('I', '1 - Marca deve funcionar apenas como intensificador'),
                ('R', '2 - Marca deve funcionar apenas como restrição'),
                ('T', '3 - Marca deve funcionar como restrição e intensificador'),
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-12 mb-3', 'autocomplete': 'off'}),
            
        }
        
        labels = {
            'idcampanha': 'Código da Campanha',
            'codmarca': 'Código da Marca',
            'tipo': 'Qual o tipo de função da marca na campanha?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['idcampanha'].queryset = Campanha.objects.all()

class ProdutosForm(forms.ModelForm):
    class Meta:
        model = Produtos
        fields = [
            'idcampanha', 'codprod', 'tipo'
        ]
        widgets = {
            'idcampanha': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'codprod': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'tipo': forms.Select(choices=[
                ('I', '1 - Produto deve funcionar apenas como intensificador'),
                ('R', '2 - Produto deve funcionar apenas como restrição'),
                ('T', '3 - Produto deve funcionar como restrição e intensificador'),
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-12 mb-3', 'autocomplete': 'off'}),
        }
        
        labels = {
            'idcampanha': 'Código da Campanha',
            'codprod': 'Código do Produto',
            'tipo': 'Qual o tipo de função do produto na campanha?'
        }

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'idcampanha', 'codfornec', 'tipo'
        ]
        widgets = {
            'idcampanha': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'codfornec': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-6 mb-3',
                'autocomplete': 'off'
            }),
            'tipo': forms.Select(choices=[
                ('I', '1 - Fornecedor deve funcionar apenas como intensificador'),
                ('R', '2 - Fornecedor deve funcionar apenas como restrição'),
                ('T', '3 - Fornecedor deve funcionar como restrição e intensificador'),
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-12 mb-3', 'autocomplete': 'off'}),
        }
        
        labels = {
            'idcampanha': 'Código da Campanha',
            'codfornec': 'Código do Fornecedor',
            'tipo': 'Qual o tipo de função do fornecedor na campanha?'
        }
        
class BlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = [
            'IDCAMPANHA', 'CODCLI', 'TIPO'
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
            }),
            'TIPO': forms.Select(choices=[
                ('B', '1 - Cliente deve ficar banido da campanha (Black List)'),
                ('W', '2 - Campanha só deve funcionar para esse cliente (White List)')
            ], attrs={'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 'classdiv': 'col-12 col-md-12 mb-3', 'autocomplete': 'off'}),
        }
        
        labels = {
            'IDCAMPANHA': 'Código da Campanha',
            'CODCLI': 'Código do Cliente',
            'TIPO': 'Qual tipo de lista o cliente deve se encaixar?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalize widgets ou outros campos se necessário