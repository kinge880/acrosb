# Generated by Django 5.0.1 on 2024-08-27 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blacklist',
            name='CPFCNPJ',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='blacklist',
            name='EMAIL',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='blacklist',
            name='NOMECLI',
            field=models.CharField(blank=True, null=True),
        ),
    ]