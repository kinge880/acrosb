from django.db import models

class BlackList(models.Model):
    IDCAMPANHA = models.IntegerField(blank=True, null=True)
    NOMECLI = models.CharField(blank=True, null=True)
    CODCLI = models.IntegerField(blank=True, null=True)
    EMAIL = models.CharField(blank=True, null=True)
    CPFCNPJ = models.CharField(blank=True, null=True)
    DTMOV = models.DateTimeField(blank=True, null=True)
                
    def __str__(self):
        return str(self.IDCAMPANHA) + ' - ' + str(self.CODCLI)
    
class Cliente(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('F', 'Física'),
        ('J', 'Jurídica'),
    ]
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    tipo_pessoa = models.CharField(max_length=1, choices=TIPO_PESSOA_CHOICES)
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    senha = models.CharField(max_length=100)  # Note: For security reasons, passwords should be hashed.

    def __str__(self):
        return self.nome