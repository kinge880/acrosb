# Generated by Django 5.0.1 on 2024-10-01 12:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0022_alter_fornecedor_idcampanha_alter_marcas_idcampanha_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklist',
            name='IDCAMPANHA',
            field=models.ForeignKey(db_column='idcampanha', on_delete=django.db.models.deletion.CASCADE, to='cpfcli.campanha'),
        ),
    ]
