from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os
from django.core.files.storage import default_storage

class empresa(models.Model):
    empresa = models.TextField(max_length=255, blank=True, null=True)
    dtcadastro = models.DateTimeField(blank=True, null=True)
    ativo = models.CharField(max_length=100, choices=[('S', 'Sim'), ('N', 'Não')], default='S')
    modulo_cliente = models.BooleanField(default='False')
    
    def __str__(self):
        return str(self.empresa)

class Cliente(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('F', 'Física'),
        ('J', 'Jurídica'),
    ]
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino')
    ]
    
    nome = models.CharField(max_length=60)
    cnpf_cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    endereco = models.CharField(max_length=40, null=True, blank=True)
    cidade = models.CharField(max_length=15, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    bairro = models.CharField(max_length=40, null=True, blank=True)
    rua = models.CharField(max_length=40, null=True, blank=True)
    numero = models.CharField(max_length=6, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    tipo_pessoa = models.CharField(max_length=1, choices=TIPO_PESSOA_CHOICES, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, null=True, blank=True)
    senha = models.CharField(max_length=100, null=True, blank=True)  # Note: For security reasons, passwords should be hashed.'
    codcli =  models.BigIntegerField(null=True, blank=True)
    ieent = models.CharField(max_length=15, null=True, blank=True)
    codativ = models.IntegerField(null=True, blank=True)
    ibge = models.IntegerField(null=True, blank=True)
    aceita_comunicacao = models.BooleanField(default=False)
    concordo_regulamento = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.nome)

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    idempresa = models.ForeignKey(empresa, on_delete=models.CASCADE)

    def __str__(self) :
        return str(self.idempresa) + ' - ' + str(self.user)


def get_image_upload_path(instance, filename):
    # Obtém o idempresa da instância
    idempresa = instance.idempresa.id if instance.idempresa else 'default'
    # Cria um caminho no formato "idempresa/filename"
    return os.path.join(str(idempresa), filename)

class PresentationSettings(models.Model):
    idempresa = models.ForeignKey('empresa', db_column='idempresa', on_delete=models.CASCADE)
    background_type = models.CharField(max_length=10, choices=[
        ('color', 'Cor'),
        ('url', 'Imagem'),
        ('urlf', 'Imagem com filtro'),
        ('colorf', 'Cor com filtro')
    ], blank=True, null=True)
    background_color = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #FFFFFF
    background_url = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    background_type_mobile = models.CharField(max_length=10, choices=[
        ('color', 'Cor'),
        ('url', 'Imagem'),
        ('urlf', 'Imagem com filtro'),
        ('colorf', 'Cor com filtro')
    ], blank=True, null=True)
    background_url_mobile = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    background_color_mobile = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #FFFFFF
    filter_color = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #000000
    filter_color_mobile = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #000000
    initial_text = models.TextField(blank=True, null=True)
    logo_type = models.CharField(max_length=10, choices=[
        ('text', 'Texto'),
        ('image', 'Imagem')
    ], default='text')
    logo_text = models.CharField(max_length=255, blank=True, null=True)
    logo_image = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    logo_type_mobile = models.CharField(max_length=10, choices=[
        ('text', 'Texto'),
        ('image', 'Imagem')
    ], default='text')
    logo_text_mobile = models.CharField(max_length=255, blank=True, null=True)
    logo_image_mobile = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    
    client_title = models.CharField(max_length=255, blank=True, null=True)
    client_subtitle = models.CharField(max_length=255, blank=True, null=True)
    client_background_type = models.CharField(max_length=10, choices=[
        ('color', 'Cor'),
        ('url', 'Imagem'),
        ('urlf', 'Imagem com filtro'),
        ('colorf', 'Cor com filtro')
    ], blank=True, null=True)
    client_background_color = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #FFFFFF
    client_background_url = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    client_background_type_mobile = models.CharField(max_length=10, choices=[
        ('color', 'Cor'),
        ('url', 'Imagem'),
        ('urlf', 'Imagem com filtro'),
        ('colorf', 'Cor com filtro')
    ], blank=True, null=True)
    client_background_url_mobile = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True)
    client_background_color_mobile = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #FFFFFF
    client_filter_color = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #000000
    client_filter_color_mobile = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #000000
    
    def __str__(self):
        return 'Configurações de Apresentação'
    