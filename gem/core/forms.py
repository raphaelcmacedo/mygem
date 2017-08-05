from django import forms

from gem.core.models import Categoria


class HomeForm(forms.Form):
     bruto = forms.DecimalField(max_digits=6, decimal_places=2)
     ouro = forms.DecimalField(max_digits=6, decimal_places=2)
     categoria = forms.ModelChoiceField(queryset=Categoria.objects.all())
     camadasProduto = forms.IntegerField(label="Camadas do Produto")
     camadasMaoDeObra = forms.IntegerField(label="Camadas de Mão de Obra", initial=3)
     peso = forms.DecimalField(max_digits=6, decimal_places=2)
     custo = forms.DecimalField(max_digits=6, decimal_places=2, disabled=True)



