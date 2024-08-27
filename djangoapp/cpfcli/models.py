from django.db import models

class BlackList(models.Model):
    IDCAMPANHA = models.IntegerField(blank=True, null=True)
    NOMECLI = models.CharField(blank=True, null=True)
    CODCLI = models.IntegerField(blank=True, null=True)
    EMAIL = models.CharField(blank=True, null=True)
    CPFCNPJ = models.CharField(blank=True, null=True)
    DTMOV = models.DateTimeField(blank=True, null=True)
                
    def __str__(self):
        return str(self.IDCAMPANHA) + ' - ' + str(self.CODPROD)