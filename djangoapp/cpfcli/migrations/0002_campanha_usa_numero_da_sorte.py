# Generated by Django 5.0.1 on 2024-09-15 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campanha',
            name='usa_numero_da_sorte',
            field=models.CharField(default='S', max_length=1),
        ),
    ]
