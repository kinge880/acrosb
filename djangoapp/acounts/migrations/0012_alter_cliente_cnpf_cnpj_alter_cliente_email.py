# Generated by Django 5.0.1 on 2024-09-21 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acounts', '0011_cliente_alter_profile_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='cnpf_cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
    ]
