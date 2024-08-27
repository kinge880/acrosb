from django.db import models

# Create your models here.
class Report(models.Model):
    descricao = models.TextField(max_length=255, blank=True, null=True)
    dtmov = models.DateTimeField(blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
                
    def __str__(self):
        return str(self.descricao)