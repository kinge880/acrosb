from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class empresa(models.Model):
    empresa = models.TextField(max_length=255, blank=True, null=True)
    dtcadastro = models.DateTimeField(blank=True, null=True)
    ativo = models.CharField(max_length=100, choices=[('S', 'Sim'), ('N', 'Não')], default='S')
    
    def __str__(self):
        return 'empresas cadastradas'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    idempresa = models.ForeignKey(empresa, on_delete=models.CASCADE)

    def __str__(self) :
        return self.idempresa
    
class PresentationSettings(models.Model):
    idempresa = models.ForeignKey(empresa, db_column='idempresa', on_delete=models.CASCADE)
    background_type = models.CharField(max_length=10, choices=[('color', 'Cor'), ('url', 'URL')], blank=True, null=True)
    background_color = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #FFFFFF
    background_url = models.ImageField( blank=True, null=True)
    filter_color = models.CharField(max_length=7, blank=True, null=True)  # Exemplo: #000000
    initial_text = models.TextField(blank=True, null=True)
    logo_type = models.CharField(max_length=10, choices=[('text', 'Texto'), ('image', 'Imagem')], default='text')
    logo_text = models.CharField(max_length=255, blank=True, null=True)
    logo_image = models.ImageField( blank=True, null=True)

    def save(self, *args, **kwargs):
        self.logo_image.name = f'logos/{self.idempresa.id}/logo.png'
        self.background_url.name = f'background/{self.idempresa.id}/background.png'
        
        super().save(*args, **kwargs)
                
    def __str__(self):
        return 'Configurações de Apresentação'
    