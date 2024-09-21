# Generated by Django 5.0.1 on 2024-09-15 17:41

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IDCAMPANHA', models.IntegerField(default=0)),
                ('NOMECLI', models.CharField(default='Sem nome cadastrado')),
                ('CODCLI', models.IntegerField(default=0)),
                ('EMAIL', models.CharField(default='Sem email cadastrado')),
                ('CPFCNPJ', models.CharField(default='Sem cpf ou cnpj cadastrado')),
                ('DTMOV', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Campanha',
            fields=[
                ('idcampanha', models.AutoField(primary_key=True, serialize=False)),
                ('descricao', models.CharField(max_length=100)),
                ('dtultalt', models.DateTimeField()),
                ('dtinit', models.DateField()),
                ('dtfim', models.DateField()),
                ('multiplicador', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('usafornec', models.CharField(default='N', max_length=1)),
                ('usamarca', models.CharField(default='N', max_length=1)),
                ('usaprod', models.CharField(default='N', max_length=1)),
                ('ativo', models.CharField(max_length=1)),
                ('dtexclusao', models.DateTimeField(blank=True, null=True)),
                ('enviaemail', models.CharField(default='S', max_length=1)),
                ('tipointensificador', models.CharField()),
                ('fornecvalor', models.IntegerField(error_messages={'min_value': 'O valor do fornecedor não pode ser menor que 1.'}, validators=[django.core.validators.MinValueValidator(1)])),
                ('marcavalor', models.IntegerField(error_messages={'min_value': 'O valor da marca não pode ser menor que 1.'}, validators=[django.core.validators.MinValueValidator(1)])),
                ('prodvalor', models.IntegerField(error_messages={'min_value': 'O valor do produto não pode ser menor que 1.'}, validators=[django.core.validators.MinValueValidator(1)])),
                ('acumulativo', models.CharField()),
                ('restringe_fornec', models.CharField(default='N', max_length=1)),
                ('restringe_marca', models.CharField(default='N', max_length=1)),
                ('restringe_prod', models.CharField(default='N', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='CampanhaFilial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcampanha', models.IntegerField(blank=True, null=True)),
                ('codfilial', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CampanhaProcessados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcampanha', models.IntegerField(blank=True, null=True)),
                ('numped', models.BigIntegerField(blank=True, null=True)),
                ('dtmov', models.DateTimeField(blank=True, null=True)),
                ('historico', models.TextField(blank=True, null=True)),
                ('codcli', models.IntegerField(blank=True, null=True)),
                ('geroucupom', models.TextField(blank=True, max_length=1, null=True)),
                ('geroubonus', models.TextField(blank=True, max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('telefone', models.CharField(max_length=11)),
                ('email', models.EmailField(max_length=254)),
                ('endereco', models.CharField(max_length=255)),
                ('cidade', models.CharField(max_length=100)),
                ('estado', models.CharField(max_length=2)),
                ('cep', models.CharField(max_length=10))
            ],
        ),
        migrations.CreateModel(
            name='CuponagemSaldo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codcli', models.IntegerField(db_column='codcli')),
                ('nomecli', models.TextField()),
                ('emailcli', models.TextField(blank=True, null=True)),
                ('telcli', models.TextField(blank=True, null=True)),
                ('cpf_cnpj', models.TextField(blank=True, null=True)),
                ('idcampanha', models.IntegerField(db_column='idcampanha')),
                ('saldo', models.IntegerField(db_column='saldo')),
                ('dtmov', models.DateTimeField(db_column='dtmov')),
            ],
            options={
                'verbose_name': 'Saldo de Cupom',
                'verbose_name_plural': 'Saldos de Cupons',
            },
        ),
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcampanha', models.IntegerField(default=0)),
                ('nomefornec', models.CharField(default='Sem descrição cadastrada')),
                ('codfornec', models.IntegerField(default=0)),
                ('dtmov', models.DateTimeField(blank=True, null=True)),
                ('tipo', models.CharField(default='N')),
            ],
        ),
        migrations.CreateModel(
            name='Marcas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcampanha', models.IntegerField(default=0)),
                ('nomemarca', models.CharField(default='Sem descrição cadastrada')),
                ('codmarca', models.IntegerField(default=0)),
                ('dtmov', models.DateTimeField(blank=True, null=True)),
                ('tipo', models.CharField(default='N')),
            ],
        ),
        migrations.CreateModel(
            name='Produtos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcampanha', models.IntegerField(default=0)),
                ('nomeprod', models.CharField(default='Sem descrição cadastrada')),
                ('codprod', models.IntegerField(default=0)),
                ('dtmov', models.DateTimeField(blank=True, null=True)),
                ('tipo', models.CharField(default='S')),
            ],
        ),
        migrations.CreateModel(
            name='Cuponagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dtmov', models.DateField()),
                ('numped', models.BigIntegerField()),
                ('valor', models.DecimalField(decimal_places=12, max_digits=50)),
                ('numsorte', models.BigIntegerField()),
                ('codcli', models.IntegerField()),
                ('nomecli', models.TextField()),
                ('emailcli', models.TextField(blank=True, null=True)),
                ('telcli', models.TextField(blank=True, null=True)),
                ('cpf_cnpj', models.TextField(blank=True, null=True)),
                ('dataped', models.DateField()),
                ('bonificado', models.CharField(default='N', max_length=1)),
                ('ativo', models.CharField(default='S', max_length=1)),
                ('idcampanha', models.ForeignKey(db_column='idcampanha', on_delete=django.db.models.deletion.CASCADE, to='cpfcli.campanha')),
            ],
        ),
        migrations.CreateModel(
            name='CuponagemVencedores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codcli', models.IntegerField()),
                ('dtsorteio', models.DateTimeField()),
                ('numsorteio', models.IntegerField()),
                ('idcampanha', models.ForeignKey(db_column='idcampanha', on_delete=django.db.models.deletion.CASCADE, to='cpfcli.campanha')),
                ('numsorte', models.ForeignKey(db_column='numsorte', on_delete=django.db.models.deletion.CASCADE, to='cpfcli.cuponagem')),
            ],
        ),
        migrations.AddIndex(
            model_name='cuponagem',
            index=models.Index(fields=['dtmov', 'codcli', 'idcampanha'], name='MSCUPONAGEM_DTMOV_IDX'),
        ),
        migrations.AddIndex(
            model_name='cuponagem',
            index=models.Index(fields=['numsorte'], name='MSCUPONAGEM_NUMSORTE_IDX'),
        ),
        migrations.AddIndex(
            model_name='cuponagemvencedores',
            index=models.Index(fields=['idcampanha', 'codcli'], name='idx_campanha_cliente'),
        ),
    ]
