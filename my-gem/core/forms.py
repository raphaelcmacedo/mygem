import datetime

import re
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from my-gem.core.models import Matricula, Orgao


class MatriculaListForm(forms.Form):
     exercicio = forms.IntegerField(initial=datetime.datetime.now().year)
     matricula = forms.ModelChoiceField(queryset=Matricula.objects.all())


class ContraChequeUploadForm(forms.Form):
     formato_choices =(
          ('SAPITUR', 'Sapitur'),
          ('CAMBUCI', 'Cambuci'),
          ('DIRF', 'DIRF'),
     )

     action_choices = (
         ('IMPORT', 'Importar contracheque'),
         ('REGISTER', 'Cadastrar usuários'),
     )

     orgao = forms.ModelChoiceField(label="Orgão",queryset=Orgao.objects.all())
     formato = forms.ChoiceField(formato_choices)
     action = forms.ChoiceField(action_choices, label="Ação")
     file = forms.FileField(label="Arquivo", widget=forms.ClearableFileInput(attrs={'multiple': True}))

     def __init__(self, *args, **kwargs):
         self.request = kwargs.pop('request', None)
         super(ContraChequeUploadForm, self).__init__(*args, **kwargs)

     def clean(self):
         self.cleaned_data = super().clean()
         email = self.request.user.email
         if not email:
             raise ValidationError(
                 "Este usuário não possui um e-mail cadastrado. Informe seu e-mail na seção 'Perfil' e depois tente novamente.")

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and username and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'Endereço de e-mail já utilizado para outro usuário')
        return email

class ChangePasswordForm(SetPasswordForm):
    pass
    

class UserListForm(forms.Form):
    orgao = forms.ModelChoiceField(label="Orgão", queryset=Orgao.objects.all())
    search = forms.CharField(label="Filtro", max_length=100, required=False)

class RegisterUserForm(forms.Form):
    orgao = forms.ModelChoiceField(label="Orgão", queryset=Orgao.objects.all())
    cpf = forms.CharField(11, label="CPF")
    matricula = forms.CharField(11, label="Matrícula")
    nome = forms.CharField(50, label = "Nome")
    sobrenome = forms.CharField(50,label = "Sobrenome")
    email = forms.EmailField(label="E-mail")

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf = re.sub('[\.-]', '', cpf)

        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('cpf')
        username = re.sub('[\.-]', '', username)

        if User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'Endereço de e-mail já utilizado para outro usuário')
        return email

    def clean_matricula(self):
        numero = self.cleaned_data.get('matricula')
        orgao = self.cleaned_data.get('orgao')
        if Matricula.objects.filter(numero=numero).filter(orgao=orgao).count():
            raise forms.ValidationError(u'Número de matrícula já utilizado para este orgão')
        return numero

class CheckUploadForm(forms.Form):
    mes_choices = (
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )

    orgao = forms.ModelChoiceField(label="Orgão", queryset=Orgao.objects.all())
    exercicio = forms.IntegerField(initial=datetime.datetime.now().year)
    mes = forms.ChoiceField(mes_choices)