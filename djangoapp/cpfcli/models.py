from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

class Campanha(models.Model):
    idcampanha = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=100)
    dtultalt = models.DateTimeField()
    dtinit = models.DateField()
    dtfim = models.DateField()
    multiplicador = models.IntegerField()
    valor = models.IntegerField()
    usafornec = models.CharField(max_length=1, default='N')
    usamarca = models.CharField(max_length=1, default='N')
    usaprod = models.CharField(max_length=1, default='N')
    ativo = models.CharField(max_length=1)
    dtexclusao = models.DateTimeField(null=True, blank=True)
    enviaemail = models.CharField(max_length=1, default='S')
    tipointensificador = models.CharField()
    fornecvalor = models.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={'min_value': 'O valor do fornecedor não pode ser menor que 1.'}
    )
    marcavalor = models.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={'min_value': 'O valor da marca não pode ser menor que 1.'}
    )
    prodvalor = models.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={'min_value': 'O valor do produto não pode ser menor que 1.'}
    )
    acumulativo = models.CharField()
    
    restringe_fornec = models.CharField(max_length=1, default='N')
    restringe_marca = models.CharField(max_length=1, default='N')
    restringe_prod = models.CharField(max_length=1, default='N')
    usa_numero_da_sorte = models.CharField(max_length=1, default='S')
    tipo_cluster_cliente = models.CharField(max_length=1, default='S')
    acumula_intensificadores = models.CharField(max_length=1, default='N')
    limite_intensificadores = models.IntegerField(default = 999)
    regulamento = models.TextField(max_length = 30000, blank=True, null=True)
    autorizacao_campanha = models.TextField(max_length = 1000, blank=True, null=True)
    logo_campanha = models.ImageField(upload_to='campanha/', blank=True, null=True)
    
    def save(self, *args, **kwargs):     
        self.dtultalt = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.idcampanha) + ' - ' + str(self.descricao)
        
class CampanhaFilial(models.Model):
    idcampanha = models.IntegerField(null=True, blank=True,)
    codfilial = models.CharField(null=True, blank=True, max_length=100)
    
    def __str__(self):
        return f"Campanha: {self.idcampanha} - Filial: {self.codfilial}"

class CampanhaProcessados(models.Model):
    idcampanha = models.IntegerField(null=True, blank=True)
    numped = models.BigIntegerField(null=True, blank=True)
    dtmov = models.DateTimeField(null=True, blank=True)
    historico = models.TextField(null=True, blank=True)
    codcli = models.IntegerField(null=True, blank=True)
    geroucupom = models.TextField(max_length=1, null=True, blank=True)
    geroubonus = models.TextField(max_length=1, null=True, blank=True)
    tipoprocessamento = models.CharField(max_length=1, default='A')
    
    def save(self, *args, **kwargs):     
        self.dtmov = timezone.now()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Campanha: {self.idcampanha} - pedido: {self.numped}"

class Cuponagem(models.Model):
    dtmov = models.DateField()  # Data do movimento
    numped = models.BigIntegerField(null=True, blank=True)  # Número do pedido
    numpedecf = models.IntegerField(null=True, blank=True)
    numcupom = models.IntegerField(null=True, blank=True)
    numcaixa = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=2, default='NS')
    valor = models.DecimalField(max_digits=50, decimal_places=12)  # Valor com até 38 dígitos e 12 casas decimais
    valor_total_venda_cupom = models.DecimalField(null=True, blank=True,max_digits=50, decimal_places=12)  # Valor com até 38 dígitos e 12 casas decimais
    numsorte = models.BigIntegerField(null=True, blank=True)  # Número da sorte
    codcli = models.IntegerField()  # Código do cliente
    nomecli = models.TextField()
    emailcli = models.TextField(null=True, blank=True)
    telcli = models.TextField(null=True, blank=True)
    cpf_cnpj = models.TextField(null=True, blank=True)
    dataped = models.DateField()  # Data do pedido
    bonificado = models.CharField(max_length=1, default='N')
    tipogeracao = models.CharField(max_length=1, default='A')
    qtcupons = models.IntegerField(null=True, blank=True)
    idcampanha = models.ForeignKey(Campanha, models.CASCADE, db_column='idcampanha')  # ID da campanha
    ativo = models.CharField(max_length=1, default='S')  # Ativo com padrão 'S'
    
    class Meta:
        indexes = [
            models.Index(fields=['dtmov', 'codcli', 'idcampanha'], name='MSCUPONAGEM_DTMOV_IDX'),
            models.Index(fields=['numsorte'], name='MSCUPONAGEM_NUMSORTE_IDX'),
        ]

    def __str__(self):
        return str(self.id)

class CuponagemSaldo(models.Model):
    codcli = models.IntegerField(db_column='codcli')  # Número de cliente
    nomecli = models.TextField()
    emailcli = models.TextField(null=True, blank=True)
    telcli = models.TextField(null=True, blank=True)
    cpf_cnpj = models.TextField(null=True, blank=True)
    idcampanha = models.IntegerField(db_column='idcampanha')  # Número da campanha
    saldo = models.IntegerField(db_column='saldo')  # Saldo
    dtmov = models.DateTimeField(db_column='dtmov')  # Data de movimentação

    class Meta: 
        verbose_name = 'Saldo de Cupom'
        verbose_name_plural = 'Saldos de Cupons'

    def __str__(self):
        return f"Cliente {self.codcli} - Campanha {self.idcampanha} - Saldo {self.saldo}"
    
class CuponagemVencedores(models.Model):
    idcampanha = models.ForeignKey(Campanha, on_delete=models.CASCADE, db_column='idcampanha')  # Chave estrangeira para Campanha
    codcli = models.IntegerField()  # Código do cliente
    dtsorteio = models.DateTimeField()  # Data e hora do sorteio
    numsorteio = models.IntegerField()  # Número do sorteio
    numsorte = models.ForeignKey(Cuponagem, on_delete=models.CASCADE, db_column='numsorte')  # Número da sorte

    class Meta:
        indexes = [
            models.Index(fields=['idcampanha', 'codcli'], name='idx_campanha_cliente'),  # Índice para idcampanha e codcli
        ]

    def __str__(self):
        return f"Campanha {self.idcampanha} - Cliente {self.codcli} - Número Sorteado {self.numsorte}"
    
class Marcas(models.Model):
    idcampanha = models.ForeignKey(Campanha, models.CASCADE, db_column='idcampanha')
    nomemarca = models.CharField(default='Sem descrição cadastrada')
    codmarca = models.IntegerField(default=0)
    dtmov = models.DateTimeField(null=True, blank=True)
    tipo = models.CharField(default='N')
    
    def save(self, *args, **kwargs):     
        self.dtmov = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.idcampanha) + ' - ' + str(self.nomemarca)

class Produtos(models.Model):
    idcampanha = models.ForeignKey(Campanha, models.CASCADE, db_column='idcampanha')
    nomeprod = models.CharField(default='Sem descrição cadastrada')
    codprod = models.IntegerField(default=0)
    dtmov = models.DateTimeField(null=True, blank=True)
    tipo = models.CharField(default='S')
    
    def save(self, *args, **kwargs):
        self.dtmov = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.idcampanha} - {self.codprod}'

class Fornecedor(models.Model):
    idcampanha = models.ForeignKey(Campanha, models.CASCADE, db_column='idcampanha')
    nomefornec = models.CharField(default='Sem descrição cadastrada')
    codfornec = models.IntegerField(default=0)
    dtmov = models.DateTimeField(null=True, blank=True)
    tipo = models.CharField(default='N')
    
    def save(self, *args, **kwargs):
        self.dtmov = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.idcampanha} - {self.codfornec}'

class BlackList(models.Model):
    IDCAMPANHA = models.ForeignKey(Campanha, models.CASCADE, db_column='idcampanha')
    NOMECLI = models.CharField(default='Sem nome cadastrado')
    CODCLI = models.IntegerField(default=0)
    EMAIL = models.CharField(default='Sem email cadastrado')
    CPFCNPJ = models.CharField(default='Sem cpf ou cnpj cadastrado')
    DTMOV = models.DateTimeField(null=True, blank=True)
    TIPO = models.CharField(default='N')
    
    def save(self, *args, **kwargs):     
        self.dtmov = timezone.now()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return str(self.IDCAMPANHA) + ' - ' + str(self.CODCLI)