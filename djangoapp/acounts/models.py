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
    
    def __str__(self):
        return str(self.empresa)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    
    client_title = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return 'Configurações de Apresentação'
    