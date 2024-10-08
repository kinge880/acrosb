# Generated by Django 5.0.1 on 2024-08-26 01:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empresa', models.TextField(blank=True, max_length=255, null=True)),
                ('dtcadastro', models.DateTimeField(blank=True, null=True)),
                ('ativo', models.CharField(choices=[('S', 'Sim'), ('N', 'Não')], default='S', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PresentationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background_type', models.CharField(blank=True, choices=[('color', 'Cor'), ('url', 'URL')], max_length=10, null=True)),
                ('background_color', models.CharField(blank=True, max_length=7, null=True)),
                ('background_url', models.ImageField(blank=True, null=True, upload_to='background/')),
                ('filter_color', models.CharField(blank=True, max_length=7, null=True)),
                ('initial_text', models.TextField(blank=True, null=True)),
                ('logo_type', models.CharField(choices=[('text', 'Texto'), ('image', 'Imagem')], default='text', max_length=10)),
                ('logo_text', models.CharField(blank=True, max_length=255, null=True)),
                ('logo_image', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('idempresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acounts.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idempresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acounts.empresa')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
