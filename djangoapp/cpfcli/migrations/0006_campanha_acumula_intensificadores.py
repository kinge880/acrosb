# Generated by Django 5.0.1 on 2024-09-18 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0005_blacklist_tipo_campanha_tipo_cluster_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='campanha',
            name='acumula_intensificadores',
            field=models.CharField(default='N', max_length=1),
        ),
    ]
