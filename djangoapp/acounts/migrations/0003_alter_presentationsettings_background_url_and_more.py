# Generated by Django 5.0.1 on 2024-08-26 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acounts', '0002_alter_presentationsettings_idempresa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentationsettings',
            name='background_url',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='presentationsettings',
            name='logo_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
