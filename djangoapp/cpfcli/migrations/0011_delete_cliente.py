# Generated by Django 5.0.1 on 2024-09-21 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('acounts', '0011_cliente_alter_profile_client'),
        ('cpfcli', '0010_cliente_concordo_regulamento'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Cliente',
        ),
    ]