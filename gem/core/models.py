from django.contrib.auth.models import User, Group
from django.db import models
from django.shortcuts import resolve_url
from django.db.models import signals

class Categoria (models.Model):
    descricao = models.CharField('Descrição', max_length=100)
    camadas = models.IntegerField('Camadas')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ('descricao',)


    def __str__(self):
        return self.descricao

