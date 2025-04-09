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
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2 spawselect2', 'classdiv': 'col-12  mb-3', 'required':True, 'autocomplete': 'off', 'select2Label': 'select', 'data-bs-toggle': 'tooltip'})
    )
    class Meta:
        model = Campanha
        fields = [
            'idcampanha',  'descricao', 'filial', 'usa_numero_da_sorte', 'tipo_cluster_cliente', 'dtinit', 'dtfim', 'enviaemail', 'acumulativo', 'valor', 
            'restringe_fornec', 'restringe_marca', 'restringe_prod', 'restringe_tipo_client',
            'tipointensificador', 'multiplicador', 'usafornec',  'fornecvalor', 'usamarca', 'marcavalor', 'usaprod', 'prodvalor', 'acumula_intensificadores', 'limite_intensificadores', 'mensagemcampanha', 'texto_mensagem_caixa', 'texto_cor_mensagem_caixa', 'url_mensagem_caixa',
            'logo_campanha', 'background_campanha', 'autorizacao_campanha', 'regulamento'
        ]
        widgets = {
            'idcampanha': forms.HiddenInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'descricao': forms.TextInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12', 
                'classdiv': 'col-12 col-md-12 mb-3', 
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'usa_numero_da_sorte': forms.Select(choices=[
                ('S', '1 - Deve utilizar números da sorte'),
                ('N', '2 - Deve utilizar cuponagem física no caixa'),
                ('T', '3 - Deve utilizar mensagem em tela no caixa'), 
                ('NT', '4 - Deve utilizar mensagem em tela e cuponagem física no caixa'),
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 
                'classdiv': 'col-12 col-lg-6 mb-3', 
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'tipo_cluster_cliente': forms.Select(choices=[
                ('N', '1 - Não utiliza Cluster por cliente'),
                ('B', '2 - Deve utilizar BlackList'),
                ('W', '3 - Deve utilizar WhiteList')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12', 
                'classdiv': 'col-12 col-lg-6 mb-3', 
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'dtinit': forms.DateInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'type': 'date',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'classlabel': 'user-label-date-cosmic-cascade-tetra-49m7',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'dtfim': forms.DateInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'type': 'date',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'classlabel': 'user-label-date-cosmic-cascade-tetra-49m7',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'enviaemail': forms.Select(choices=[
                ('N', '1 - Não enviar email'),
                ('S', '2 - Enviar email com números da sorte')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'acumulativo': forms.Select(choices=[
                ('N', '1 - Não acumular saldo'),
                ('S', '2 - Acumular apenas saldo acima do valor'),
                ('T', '3 - Acumular saldo em todas as vendas')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-8 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'restringe_fornec': forms.Select(choices=[
                ('N', '1 - Não utilizar restrição por fornecedor'),
                ('C', '2 - Restrição por fornecedor cadastrado')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'restringe_marca': forms.Select(choices=[
                ('N', '1 - Não utilizar restrição por marca'),
                ('C', '2 - Restrição por marca cadastrada')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'restringe_prod': forms.Select(choices=[
                ('N', '1 - Não utilizar restrição por produto'),
                ('C', '2 - Restrição por produto cadastrado')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'restringe_tipo_client': forms.Select(choices=[
                ('T', '1 - Não aplicar restrição'),
                ('F', '2 - Restringir apenas a pessoa Física'),
                ('J', '3 - Restringir apenas a pessoa Juridica')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'tipointensificador': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador'),
                ('M', '2 - Multiplicação'),
                ('S', '3 - Soma')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-8 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'multiplicador': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'usamarca': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador por marca'),
                ('C', '2 - Intensificador por marca cadastrada'),
                ('M', '3 - Intensificador por marca múltipla')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-8 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'marcavalor': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'usafornec': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador por fornecedor'),
                ('C', '2 - Intensificador por fornecedor cadastrado'),
                ('M', '3 - Intensificador por fornecedor múltiplo')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-8 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'fornecvalor': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'usaprod': forms.Select(choices=[
                ('N', '1 - Não utilizar intensificador por produto'),
                ('C', '2 - Intensificador por produto cadastrado'),
                ('M', '3 - Intensificador por produto múltiplo')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-8 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'prodvalor': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'acumula_intensificadores': forms.Select(choices=[
                ('N', '1 - Não acumular intensificadores'),
                ('S', '2 - Acumular intensificadores')
            ], attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
                'classdiv': 'col-12 col-lg-8 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'limite_intensificadores': forms.NumberInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-4 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'mensagemcampanha': forms.TextInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'texto_mensagem_caixa': forms.TextInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'url_mensagem_caixa': forms.TextInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'texto_cor_mensagem_caixa': forms.TextInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'min': '1',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'logo_campanha': forms.ClearableFileInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'autorizacao_campanha': forms.Textarea(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12 mt-5',
                'classdiv': 'col-12  mb-3',
                'autocomplete': 'off',
                'rows': 1,
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'regulamento': forms.Textarea(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12 summernote',
                'classdiv': 'col-12 mb-3',
                'rows': 1,
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            }),
            'background_campanha': forms.ClearableFileInput(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12',
                'classdiv': 'col-12 col-lg-6 mb-3',
                'autocomplete': 'off',
                'data-bs-toggle': 'tooltip',
                'data-bs-custom-class': 'custom-tooltip',
                'data-bs-placement':"bottom"
            })
        }
        
        labels = {
            'idcampanha': 'Código interno',
            'descricao': 'Descrição da campanha',
            'regulamento': 'Regulamento completo da campanha',
            'autorizacao_campanha': 'Certificado de autorização federal',
            'dtinit': 'Data inicial',
            'dtfim': 'Data final',
            'enviaemail': 'Envia email',
            'valor': 'Valor por número',
            'acumulativo': 'Acumulação de saldo entre vendas',
            'restringe_fornec': 'Restrição por fornecedor', 
            'restringe_marca': 'Restrição por marca', 
            'restringe_prod': 'Restrição por produto',
            'restringe_tipo_client': 'Restrição físico/juridico',
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
            'limite_intensificadores': 'Limite de intensificadores',
            'logo_campanha': 'Logo da campanha',
            'background_campanha': 'Background da campanha'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
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
            'codmarca': forms.Select(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12 marca',
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
            'idcampanha': 'Campanha ativa',
            'codmarca': 'Marca',
            'tipo': 'Qual o tipo de função da marca na campanha?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['idcampanha'].queryset = Campanha.objects.filter(ativo='S')
        self.fields['idcampanha'].empty_label = None  # Define o texto para quando nada for selecionado
        self.fields['idcampanha'].widget.attrs.update({
            'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
            'classdiv': 'col-12 col-md-6 mb-3',
            'autocomplete': 'off',
            'required': True
        })

class ProdutosForm(forms.ModelForm):
    class Meta:
        model = Produtos
        fields = [
            'idcampanha', 'codprod', 'tipo'
        ]
        widgets = {
            'codprod': forms.Select(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12 codprod_select',
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['idcampanha'].queryset = Campanha.objects.filter(ativo='S')
        self.fields['idcampanha'].empty_label = None  # Define o texto para quando nada for selecionado
        self.fields['idcampanha'].widget.attrs.update({
            'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
            'classdiv': 'col-12 col-md-6 mb-3',
            'autocomplete': 'off',
            'required': True
        })

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'idcampanha', 'codfornec', 'tipo'
        ]
        widgets = {
            'codfornec': forms.Select(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12 fornec',
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['idcampanha'].queryset = Campanha.objects.filter(ativo='S')
        self.fields['idcampanha'].empty_label = None  # Define o texto para quando nada for selecionado
        self.fields['idcampanha'].widget.attrs.update({
            'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
            'classdiv': 'col-12 col-md-6 mb-3',
            'autocomplete': 'off',
            'required': True
        })
        
class BlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = [
            'IDCAMPANHA', 'CODCLI', 'TIPO'
        ]
        widgets = {
            'CODCLI': forms.Select(attrs={
                'class': 'input-cosmic-cascade-tetra-49m7 form-control col-12 client_select',
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
        self.fields['IDCAMPANHA'].queryset = Campanha.objects.filter(ativo='S')
        self.fields['IDCAMPANHA'].empty_label = None  # Define o texto para quando nada for selecionado
        self.fields['IDCAMPANHA'].widget.attrs.update({
            'class': 'input-cosmic-cascade-tetra-49m7 form-select col-12',
            'classdiv': 'col-12 col-md-6 mb-3',
            'autocomplete': 'off',
            'required': True
        })