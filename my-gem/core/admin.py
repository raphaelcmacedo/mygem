from django.contrib import admin

# Register your models here.
class CategoriaModelAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'camadas']

admin.site.register(Categoria, CategoriaModelAdmin)

