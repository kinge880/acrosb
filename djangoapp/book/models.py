from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class cidades(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=150)
    uf = models.CharField(max_length=2)
    ativo = models.BooleanField(default=True)

class estados(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=150)
    uf = models.CharField(max_length=2)
    ativo = models.BooleanField(default=True)

#Tabela de perfil do usuário, serve como complemento aos dados base do django para usuários no caso nome, sobrenome, user, email, senha
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sobre = models.TextField(blank=True, null=True, max_length=1000)
    endereco = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.ForeignKey(cidades, models.RESTRICT, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    aniversario = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    cel = models.CharField(max_length=20, blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outros')], blank=True, null=True)
    twitter = models.CharField(max_length=150, blank=True, null=True)
    face = models.CharField(max_length=150, blank=True, null=True)
    linkedin = models.CharField(max_length=150, blank=True, null=True)
    instagram = models.CharField(max_length=150, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) :
        return self.user

#para guardar as regiões trabalhadas
class regional(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)

#dados referentes a primeira planilha  BOOk AGENDA
#areas de atuação
class areaAtuacao(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)

#cabeçalho geral da agenda
class agendaMes(models.Model):
    id = models.AutoField(primary_key=True)
    mesAno = models.DateField()
    id_gerente = models.ForeignKey(User, models.RESTRICT, related_name='agendaMes_gerente')
    id_gerenteGeral = models.ForeignKey(User, models.RESTRICT, related_name='agendaMes_gerenteGeral')
    area_atuacao = models.ForeignKey(areaAtuacao, models.RESTRICT, related_name='agendaMes_area_atuacao')

    class Meta:
        db_table = 'agendaMes'
    
    def __str__(self):
        return str(self.id_gerenteGeral) + ' - '+ str(self.mesAno)

#cabeçalho semanal da agenda, guardando dados gerais do vendedor para aquela semana
class agendaSemana(models.Model):
    id = models.AutoField(primary_key=True)
    dt_inicial = models.DateTimeField()
    dt_final = models.DateTimeField(blank=True, null=True)
    id_vendedor = models.ForeignKey(User, models.RESTRICT)
    motivo_escolha = models.TextField(max_length=500, blank=True, null=True)
    objetivo_principal = models.TextField(max_length=500, blank=True, null=True)
    alteracoes = models.TextField(max_length=500, blank=True, null=True)
    idagenda_mes = models.ForeignKey(agendaMes, models.RESTRICT)

    class Meta:
        db_table = 'agendaSemana'
    
    def __str__(self):
        return str(self.id_vendedor) + ' - '+ str(self.dt_inicial) + ' - '+ str(self.dt_final)

#agenda do dia, aqui é onde vai ser guardado a exeução dela, com a hora inicial e final e a avaliação realizada
class agendaDia(models.Model):
    id = models.AutoField(primary_key=True)
    dia = models.CharField(max_length=20)
    hora_inicial = models.TimeField()
    hora_final = models.TimeField()
    pauta = models.CharField(max_length=150)
    realizado = models.BooleanField(blank=True, null=True)
    id_agenda_semana = models.ForeignKey(agendaSemana, models.RESTRICT, related_name='agendaDia_agenda_semana')

    class Meta:
        db_table = 'agendaDia'
    
    def __str__(self):
        return str(self.id_agenda_semana) + ' - '+ str(self.dia)

#Tabelas da segunda planiha Analise_API
class pilaresQuinzenais(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.descricao)

#guarda as perguntas do questionamento, podendo reutilizar ela em diversos questionamentos diferentes
class questionamentosQuinzenais(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=150)
    id_pilar = models.ForeignKey(pilaresQuinzenais, models.RESTRICT, related_name='questionamentosQuinzenais_pilar')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return str(self.descricao)

#cabeçalho da analise quinzenal
class analiseQuinzenal(models.Model):
    id = models.AutoField(primary_key=True)
    mes_ano = models.DateField()
    quinzena = models.IntegerField(default = 1)
    id_gerente = models.ForeignKey(User, models.RESTRICT, related_name='analiseQuinzenal_gerente')
    id_gerente_geral = models.ForeignKey(User, models.RESTRICT, related_name='analiseQuinzenal_gerenteGeral')
    id_vendedor = models.ForeignKey(User, models.RESTRICT, related_name='analiseQuinzenal_vendedor')

    def __str__(self):
        return str(self.mes_ano) + ' - '+ str(self.id_gerente) + ' - '+ str(self.id_vendedor)

#questionamentos realizados na análise, aqui vamos utilizar os questionamentos e linkar eles a respostas, observações, e se foi ou não realizado
class questRealizados(models.Model):
    id = models.AutoField(primary_key=True)
    id_quest = models.ForeignKey(questionamentosQuinzenais, models.RESTRICT, related_name='questRealizados_quest')
    id_analise = models.ForeignKey(analiseQuinzenal, models.RESTRICT, related_name='questRealizados_analise')
    observacao = models.TextField(max_length=1000, blank=True, null=True)
    realizado = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + ' - ' + str(self.id_quest)

#dados para a planilha 3 BR Reuniões
#cadastro de fornecedor no sistema
class fornecedor(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(max_length=300)
    contato_fornec = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.ForeignKey(cidades, models.RESTRICT, blank=True, null=True)
    estado = models.ForeignKey(estados, models.RESTRICT, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    cgc = models.CharField(max_length=20, blank=True, null=True)
    bairro = models.CharField(max_length=50, blank=True, null=True)
    dt_bloqueio = models.DateField(blank=True, null=True)
    obs = models.TextField(max_length=300, blank=True, null=True)
    repre = models.TextField(max_length=300, blank=True, null=True)
    repre_cel = models.CharField(max_length=20, blank=True, null=True)
    repre_email = models.CharField(max_length=50, blank=True, null=True)
    rep_contato = models.CharField(max_length=100, blank=True, null=True)
    rep_endereco = models.CharField(max_length=100, blank=True, null=True)
    rep_bairro = models.CharField(max_length=50, blank=True, null=True)
    rep_cidade = models.ForeignKey(cidades, models.RESTRICT, blank=True, null=True, related_name='rep_cidade')
    rep_uf = models.CharField(max_length=2, blank=True, null=True)
    rep_cep = models.CharField(max_length=10, blank=True, null=True)
    dt_cadastro = models.DateField(blank=True, null=True)
    dt_exclusao = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.descricao

#cabeçalho da reunião
class reuniao(models.Model):
    id = models.AutoField(primary_key=True)
    local = models.CharField(max_length = 150, blank=True, null=True)
    data = models.DateField()
    executo = models.ForeignKey(User, models.RESTRICT, related_name='reuniao_executo')
    horaInicial = models.TimeField(blank=True, null=True)
    horaFinal = models.TimeField(blank=True, null=True)
    tipoReuniao = models.CharField()
    consideracao_final = models.TextField(max_length = 3000, blank=True, null=True)
    assinatura_supervisor = models.CharField(max_length = 150, blank=True, null=True)
    assinatura_lider = models.CharField(max_length = 150, blank=True, null=True)

    def __str__(self):
        return str(self.id) + ' - ' + str(self.executo)

#lista de participantes, aqui pode se ter um usuário como participante ou um fornecedor, por isso as chaves estrangeiras de ambos são opcionais já que ou é um ou outro
class participantes(models.Model):
    id = models.AutoField(primary_key=True)
    e_convidado = models.BooleanField(default = False)
    id_user = models.ForeignKey(User, models.RESTRICT, blank=True, null=True, related_name='participantes_user')
    id_fornecedor = models.ForeignKey(User, models.RESTRICT, blank=True, null=True, related_name='participantes_fornecedor')
    assunto = models.TextField(max_length = 500, blank=True, null=True)
    participou = models.BooleanField(blank=True, null=True)
    id_reniao = models.ForeignKey(reuniao, models.CASCADE, related_name='participantes_reniao')
    assinatura = models.CharField(max_length = 150, blank=True, null=True)

    def __str__(self):
        return self.id

#as pautas na reunião com descrição e solução
class pautas(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(max_length = 1500, blank=True, null=True)
    solucao = models.TextField(max_length = 1500, blank=True, null=True)
    id_reniao = models.ForeignKey(reuniao, models.CASCADE, related_name='pautas_reniao')

    def __str__(self):
        return self.descricao
    
#tabelas para a quarta planilha, execução
#cabeçalho geral para a tabela de execução
class execucao(models.Model):
    id = models.AutoField(primary_key=True)
    id_regional = models.ForeignKey(regional, models.RESTRICT, related_name='execucao_regional')
    id_vendedor = models.ForeignKey(User, models.RESTRICT, related_name='execucao_vendedor')
    id_supervisor = models.ForeignKey(User, models.RESTRICT, related_name='execucao_supervisor')
    dt_aval = models.DateField()
    pdv = models.IntegerField(blank=True, null=True)
    cod_fantasia = models.CharField(max_length = 150)
    fat_anterior = models.FloatField(blank=True, null=True)
    fat_atual = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.id

#perguntas que podem ser reutilizadas na execução
class perguntasExecucao(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(max_length = 300)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.descricao

class pdv(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(max_length = 300)
    cod_pdv = models.IntegerField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.descricao

class resultadoExecucao(models.Model):
    id = models.AutoField(primary_key=True)
    id_execucao = models.ForeignKey(execucao, models.CASCADE, related_name='resultadoExecucao_execucao')
    id_pdv = models.ForeignKey(pdv, models.CASCADE, related_name='resultadoExecucao_pdv')
    id_perguntas_execucao = models.ForeignKey(perguntasExecucao, models.CASCADE, related_name='resultadoExecucao_perguntas_execucao')
    executado = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.id

class observacoesExecucao(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_obs = models.CharField(max_length = 2)
    descricao = models.TextField(max_length = 300)
    id_execucao = models.ForeignKey(execucao, models.CASCADE, related_name='observacoesExecucao_execucao')

    def __str__(self):
        return self.descricao


#planilha 5 treinamentos

class cliente(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    cidade = models.ForeignKey(cidades, models.RESTRICT, blank=True, null=True, related_name='cliente_cidade')
    estado = models.ForeignKey(estados, models.RESTRICT, blank=True, null=True, related_name='cliente_estado')
    cep = models.CharField(max_length=10, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    observacoes = models.TextField(max_length=5000, blank=True, null=True)
    cnpj = models.CharField(max_length=50, blank=True, null=True)
    cpf = models.CharField(max_length=50, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class rotas(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(max_length = 150)
    dt_inicial = models.DateField(blank=True, null=True)
    dt_final = models.DateField(blank=True, null=True)
    representante = models.ForeignKey(User, on_delete=models.RESTRICT, blank=True, null=True, related_name='rotas_representante')
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.descricao

class rotasClientes(models.Model):
    id = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(cliente, on_delete=models.CASCADE, related_name='rotasClientes_cliente')
    id_rota = models.ForeignKey(rotas, on_delete=models.CASCADE, related_name='rotasClientes_rota')

    def __str__(self):
        return self.id

class avaliacaoPerguntas(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(max_length = 150)
    passo = models.IntegerField()
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.descricao

class avaliacao(models.Model):
    id = models.AutoField(primary_key=True)
    id_rota = models.ForeignKey(rotas, on_delete=models.CASCADE, related_name='avaliacao_rota')
    id_avaliador = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='avaliacao_avaliador')
    id_avaliado = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='avaliacao_avaliado')
    dt_inicial = models.DateField(blank=True, null=True)
    dt_final = models.DateField(blank=True, null=True)
    pontos_fortes = models.TextField(max_length = 5000, blank=True, null=True)
    pontos_a_desenvolver = models.TextField(max_length = 5000, blank=True, null=True)
    assinatura_avaliador = models.TextField(max_length = 5000, blank=True, null=True)
    assinatura_avaliado = models.TextField(max_length = 5000, blank=True, null=True)
    fat_ant = models.FloatField(blank=True, null=True)
    fat_antual = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.id

class avaliacaoitems(models.Model):
    id = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(cliente, on_delete=models.RESTRICT, related_name='avaliacaoitems_cliente')
    id_avaliacao = models.ForeignKey(rotas, on_delete=models.CASCADE, related_name='avaliacaoitems_avaliacao')
    id_avaliacao_perguntas = models.ForeignKey(avaliacaoPerguntas, on_delete=models.CASCADE, related_name='avaliacaoitems_avaliacao_perguntas')
    realizado = models.BooleanField(blank=True, null=True)
    dt_treino = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + ' - ' + str(self.id_avaliacao)

#planilha 6 anotações
class anotacoes(models.Model):
    id = models.AutoField(primary_key=True)
    vdd = models.IntegerField()
    cidade = models.ForeignKey(cidades, models.RESTRICT, blank=True, null=True, related_name='anotacoes_cidade')
    id_avaliador = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='anotacoes_avaliador')
    id_avaliado = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='anotacoes_avaliado')
    dt_inicial = models.DateField(blank=True, null=True)
    dt_final = models.DateField(blank=True, null=True)
    anotacoes = models.TextField(max_length = 15000, blank=True, null=True)
    obs = models.TextField(max_length = 10000, blank=True, null=True)
    image = models.ImageField(upload_to ='uploads/% Y/% m/% d/', blank=True, null=True) 

    def __str__(self):
        return str(self.cidade) + ' - ' + str(self.id)

#planilha 7 10+

class visitaClientes(models.Model):
    id = models.AutoField(primary_key=True)
    dt_inicial = models.DateField(blank=True, null=True)
    dt_final = models.DateField(blank=True, null=True)
    cidade = models.ForeignKey(cidades, models.RESTRICT, blank=True, null=True, related_name='visitaClientes_cidade')
    id_avaliador = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='visitaClientes_avaliador')
    id_avaliado = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='visitaClientes_avaliado')

class visitaClientesItems(models.Model):
    id = models.AutoField(primary_key=True)
    id_visita = models.ForeignKey(visitaClientes, on_delete=models.CASCADE, related_name='visitaClientesItems_visita')
    id_cliente = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='visitaClientesItems_cliente')
    id_comprador = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='visitaClientesItems_comprador')
    objetivo = models.TextField(max_length = 5000, blank=True, null=True)
    status = models.TextField(max_length = 5000, blank=True, null=True)
    ult_compra = models.FloatField(blank=True, null=True)
    negociacao_atual = models.FloatField(blank=True, null=True)
    tipo_cliente = models.CharField()

    def __str__(self):
        return self.id
    
#planilha 10 oportunidades
class oportunidades(models.Model):
    id = models.AutoField(primary_key=True)
    id_avaliado = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='oportunidades_avaliado')
    id_avaliador = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='oportunidades_avaliador')
    dt_inicial = models.DateField(blank=True, null=True)
    dt_final = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.id
    
class oportunidadeItems(models.Model):
    id = models.AutoField(primary_key=True)
    id_oportunidades = models.ForeignKey(oportunidades, on_delete=models.CASCADE, related_name='oportunidadeItems_oportunidades')
    oque = models.TextField(max_length = 1500, blank=True, null=True)
    como = models.TextField(max_length = 1500, blank=True, null=True)
    quando = models.DateField(blank=True, null=True)
    resultado = models.TextField(max_length = 1500, blank=True, null=True)
    reprogramacao = models.BooleanField(default = False)
    dt_reprogramacao = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to ='uploads/% Y/% m/% d/', blank=True, null=True)

    def __str__(self):
        return self.id
    
#planilha 11 problemas e soluções
class problemasSolucoes(models.Model):
    id = models.AutoField(primary_key=True)
    id_avaliado = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='problemasSolucoes_avaliado')
    id_avaliador = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='problemasSolucoes_avaliador')
    dt_inicial = models.DateField(blank=True, null=True)
    dt_final = models.DateField(blank=True, null=True)
    obs = models.TextField(max_length = 5000, blank=True, null=True)

    def __str__(self):
        return self.id

class problemasSolucoesItems(models.Model):
    id = models.AutoField(primary_key=True)
    id_problemas_solucoes = models.ForeignKey(problemasSolucoes, on_delete=models.CASCADE, related_name='problemasSolucoesItems_problemas_solucoes')
    problema = models.TextField(max_length = 1500, blank=True, null=True)
    solucao = models.TextField(max_length = 1500, blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length = 2, blank=True, null=True)
    resolvido = models.BooleanField(default = False)

    def __str__(self):
        return self.id