# Generated by Django 5.0.1 on 2024-09-22 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpfcli', '0011_delete_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='campanha',
            name='logo_campanha',
            field=models.ImageField(blank=True, null=True, upload_to='campanha/logo/'),
        ),
    ]
