# Generated by Django 5.0.1 on 2024-09-25 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0016_campanha_autorizacao_campanha_campanha_regulamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='campanha',
            name='limite_intensificadores',
            field=models.IntegerField(default=999),
        ),
    ]