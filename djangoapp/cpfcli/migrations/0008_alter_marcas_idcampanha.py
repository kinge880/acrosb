# Generated by Django 5.0.1 on 2024-09-09 01:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0007_marcas_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marcas',
            name='idcampanha',
            field=models.ForeignKey(db_column='idcampanha', on_delete=django.db.models.deletion.CASCADE, to='cpfcli.campanha'),
        ),
    ]
