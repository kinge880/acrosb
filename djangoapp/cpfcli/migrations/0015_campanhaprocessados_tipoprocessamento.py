# Generated by Django 5.0.1 on 2024-09-23 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0014_cuponagem_bonificado'),
    ]

    operations = [
        migrations.AddField(
            model_name='campanhaprocessados',
            name='tipoprocessamento',
            field=models.CharField(default='A', max_length=1),
        ),
    ]
