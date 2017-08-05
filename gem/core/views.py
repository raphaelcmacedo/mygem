from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from gem.core.forms import HomeForm

@login_required
def home (request):
    if request.method == 'POST':
        # Busca os dados do form
        form = HomeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            bruto = data['bruto']


    else:
        form = HomeForm()

    context = {'form': form}

    return render(request, 'index.html', context)



