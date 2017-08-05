from django.contrib import admin
from gem.core.models import Categoria


class CategoriaModelAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'camadas']

admin.site.register(Categoria, CategoriaModelAdmin)

