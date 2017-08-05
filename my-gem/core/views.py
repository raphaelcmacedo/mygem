from _thread import start_new_thread

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from my-gem.core import util
from my-gem.core.forms import MatriculaListForm, ContraChequeUploadForm, UserForm, UserListForm, RegisterUserForm, \
    ChangePasswordForm, CheckUploadForm
from my-gem.core.models import Matricula, ContraCheque, Gestor, Orgao
from my-gem.core.services import upload_contra_cheques, \
    upload_contra_cheques_async
from my-gem.core.tables import UserTable
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

@login_required
def home (request):
    if request.user.is_change_password():
        uidb64 = urlsafe_base64_encode(force_bytes(request.user.pk))
        token = default_token_generator.make_token(request.user)
        return HttpResponseRedirect(reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token}))

    contra_cheques = []

    if request.method == 'POST':
        # Busca os dados do form
        form = MatriculaListForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            matricula = data['matricula']
            exercicio = data['exercicio']

        contra_cheques = list(ContraCheque.objects.contracheques_by_matricula(matricula, exercicio))
    else:
        form = MatriculaListForm()


    # Matrícula
    orgaosGestor = Gestor.objects.gestor_by_user(request.user)
    matriculas = Matricula.objects.none()
    # Verifica se o usuário é gestor de algum orgão (um ou mais), caso seja busca todas as matrículas desse orgão
    if orgaosGestor:
        for gestor in orgaosGestor:
            matriculas = matriculas | Matricula.objects.matriculas_by_orgao(gestor.orgao)
    else:
        matriculas = Matricula.objects.matriculas_by_user(request.user)
    form.fields["matricula"].queryset = matriculas

    context = {'form': form, 'contra_cheques':contra_cheques}

    return render(request, 'index.html', context)



@login_required
def upload_contra_cheque(request):
    # Matrícula
    orgaosGestor = Gestor.objects.gestor_by_user(request.user)
    orgaos = Orgao.objects.none()
    # Verifica se o usuário é gestor de algum orgão (um ou mais), caso seja busca todas as matrículas desse orgão
    if orgaosGestor:
        for gestor in orgaosGestor:
            orgaos = orgaos | Orgao.objects.filter(id = gestor.orgao.id)

    if request.method == 'POST':
        form = ContraChequeUploadForm(request.POST, request.FILES, request = request)
        form.fields["orgao"].queryset = orgaos

        if form.is_valid():
            files = request.FILES.getlist('file')
            background = False

            tempfiles = []
            for f in files:
                # Arquivo temporário
                tmp = util.create_temp_file(f)
                tempfiles.append(tmp)

            if len(files) > 10:
                background = True
                sucesses = []
                failures = []
                email = request.user.email
                #if not email:
                #    raise ValidationError("Este usuário não possui um e-mail cadastrado. Informe seu e-mail na seção 'Perfil' e depois tente novamente.")

                start_new_thread(upload_contra_cheques_async, (form, tempfiles,email,))
            else:
                result = upload_contra_cheques(form, tempfiles)
                sucesses = result[0]
                failures = result[1]
            return render(request, 'contra_cheque/success.html', {'sucesses': sucesses, 'failures': failures, 'background': background})

    else:
        form = ContraChequeUploadForm()
        form.fields["orgao"].queryset = orgaos
    return render(request, 'contra_cheque/upload.html', {'form': form})

def edit_user(request, pk = None, template_name="registration/edit_user.html"):
    if pk is None:
        user = request.user
    else:
        user = User.objects.all().filter(pk = pk).first()

    if request.method == "POST":
        form = UserForm(data=request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            url = reverse('home')
            return HttpResponseRedirect(url)
    else:
        form = UserForm(instance=user)

    context = {'form': form}
    return render(request, template_name, context)

def change_password(request, pk = None, template_name="registration/password_user.html"):
    if pk is None:
        user = request.user
    else:
        user = User.objects.all().filter(pk = pk).first()

    if request.method == "POST":
        form = ChangePasswordForm(data=request.POST, user=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            url = reverse('home')
            return HttpResponseRedirect(url)
    else:
        form = ChangePasswordForm(user=user)

    context = {'form': form}
    return render(request, template_name, context)


@login_required
def list_user (request):

    qs = User.objects.none()

    orgaosGestorIds = Gestor.objects.gestor_by_user(request.user).values_list('orgao__id', flat=True)
    orgaosQuerySet = Orgao.objects.filter(id__in=orgaosGestorIds)

    if request.method == 'POST':
        # Busca os dados do form
        form = UserListForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            orgao = data['orgao']
            search = data['search']
            ids = Matricula.objects.filter(orgao=orgao).values_list('id', flat=True)
            qs = User.objects.filter(matricula__in=ids).distinct()
            if search:
                for term in search.split():
                    qs = qs.filter(Q(username=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term))

    else:
        # Matrícula
        form = UserListForm()

    table = UserTable(qs)

    if not Gestor.objects.gestor_can_change_password(request.user):
        table.exclude = ('senha',)

    form.fields["orgao"].queryset = orgaosQuerySet
    context = {'form': form, 'table':table}

    return render(request, 'registration/list_user.html', context)

@transaction.atomic
def register_user(request, template_name="registration/register_user.html"):
    if request.method == "POST":
        form = RegisterUserForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            orgao = data['orgao']
            cpf = data['cpf']
            numero_matricula = data['matricula']
            nome = data['nome']
            sobrenome = data['sobrenome']
            email = data['email']

            # Verifica se esse cpf já possui um usuário caso contrário cadastra
            try:
                user = User.objects.get(username=cpf)
            except ObjectDoesNotExist:
                user = User()
                user.username = cpf
                user.password = make_password(numero_matricula)
                user.first_name = nome
                user.last_name = sobrenome
                user.email = email
                user.save()

            matricula = Matricula()
            matricula.user = user
            matricula.orgao = orgao
            matricula.numero = numero_matricula
            matricula.save()

            url = reverse('list_user')
            return HttpResponseRedirect(url)
    else:
        form = RegisterUserForm()

    context = {'form': form}
    return render(request, template_name, context)

@login_required
def check_upload (request):

    qs = User.objects.none()

    orgaosGestorIds = Gestor.objects.gestor_by_user(request.user).values_list('orgao__id', flat=True)
    orgaosQuerySet = Orgao.objects.filter(id__in=orgaosGestorIds)

    if request.method == 'POST':
        # Busca os dados do form
        form = CheckUploadForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            orgao = data['orgao']
            exercicio = data['exercicio']
            mes = data['mes']

            idsMatriculaOrgao = Matricula.objects.filter(orgao=orgao).values_list('id', flat=True)
            idsMatriculaContracheque = ContraCheque.objects.filter(matricula__orgao=orgao).filter(mes=mes).filter(exercicio=exercicio).values_list('matricula_id', flat=True)
            qs = User.objects.filter(matricula__in=idsMatriculaOrgao).exclude(matricula__in=idsMatriculaContracheque).distinct()


    else:
        # Matrícula
        form = CheckUploadForm()

    table = UserTable(qs)
    table.exclude = ('senha',)

    form.fields["orgao"].queryset = orgaosQuerySet
    context = {'form': form, 'table':table}

    return render(request, 'contra_cheque/check_upload.html', context)