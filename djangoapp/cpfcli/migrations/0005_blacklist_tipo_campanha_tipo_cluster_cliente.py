# Generated by Django 5.0.1 on 2024-09-17 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0004_alter_cuponagem_numped_alter_cuponagem_numsorte'),
    ]

    operations = [
        migrations.AddField(
            model_name='blacklist',
            name='TIPO',
            field=models.CharField(default='N'),
        ),
        migrations.AddField(
            model_name='campanha',
            name='tipo_cluster_cliente',
            field=models.CharField(default='S', max_length=1),
        ),
    ]