# Generated by Django 5.0.1 on 2024-09-01 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0002_blacklist_cpfcnpj_blacklist_email_blacklist_nomecli'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('cnpf_cnpj', models.CharField(max_length=18, unique=True)),
                ('telefone', models.CharField(max_length=11)),
                ('email', models.EmailField(max_length=254)),
                ('endereco', models.CharField(max_length=255)),
                ('cidade', models.CharField(max_length=100)),
                ('estado', models.CharField(max_length=2)),
                ('bairro', models.CharField(max_length=150)),
                ('rua', models.CharField(max_length=150)),
                ('numero', models.CharField(max_length=8)),
                ('cep', models.CharField(max_length=10)),
                ('tipo_pessoa', models.CharField(choices=[('F', 'Física'), ('J', 'Jurídica')], max_length=1)),
                ('data_nascimento', models.DateField()),
                ('genero', models.CharField(choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')], max_length=1)),
                ('senha', models.CharField(max_length=100)),
            ],
        ),
    ]
