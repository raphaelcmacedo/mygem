# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-05 20:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=100, verbose_name='Descrição')),
                ('camadas', models.IntegerField(verbose_name='Camadas')),
            ],
            options={
                'verbose_name_plural': 'Categorias',
                'verbose_name': 'Categoria',
                'ordering': ('descricao',),
            },
        ),
    ]
