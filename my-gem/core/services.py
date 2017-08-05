from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from my-gem.core.connectors.cambuci import read_matricula_cambuci, read_contra_cheque_cambuci
from my-gem.core.connectors.dirf import read_informe_rendimento
from my-gem.core.connectors.sapitur import read_contra_cheque_sapitur, read_matricula_sapitur
from my-gem.core.google import insert_file
from my-gem.core.models import Matricula


def _send_email(email_to, sucesses, failures):
    subject = 'Confirmação de processamento dos contracheques'
    message = render_to_string('contra_cheque/success_email.txt', {"sucesses":sucesses, "failures":failures})
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email_to]
    mail.send_mail(subject, message, from_email, to)

def upload_contra_cheques_async(form, files, email_to):
    result = upload_contra_cheques(form, files)
    sucesses = result[0]
    failures = result[1]
    _send_email(email_to, sucesses, failures)

def upload_contra_cheques(form, files):
    sucesses = []
    failures = []

    if form.is_valid():

        data = form.cleaned_data
        formato = data['formato']
        action = data['action']
        orgao = data['orgao']

        matriculas_dict = Matricula.objects.matriculas_dict_by_orgao(orgao)

        for f in files:
            try:
                if action == 'IMPORT':
                    contra_cheque = upload_contra_cheque_file(f, orgao, formato, matriculas_dict)
                    sucesses.append('O arquivo {} foi importado com sucesso.'.format(f["name"]))
                elif action == 'REGISTER':
                    matricula = register_matricula(f, orgao, formato)
                    if matricula:
                        sucesses.append('A matrícula {} foi cadastrada pelo arquivo {}.'.format(str(matricula), f["name"]))

            except Exception as e:
                failures.append('O arquivo {} gerou o seguinte erro: {}'.format(f["name"], str(e)))

    result = (sucesses, failures)
    return result

def upload_contra_cheque_file(f, orgao, formato, matriculas_dict):

    contra_cheques = []
    if formato == 'SAPITUR':
        contra_cheque = read_contra_cheque_sapitur(f, matriculas_dict)
        contra_cheques.append(contra_cheque)
    elif formato == 'CAMBUCI':
        contra_cheque = read_contra_cheque_cambuci(f, matriculas_dict)
        contra_cheques.append(contra_cheque)
    elif formato == 'DIRF':
        contra_cheques = read_informe_rendimento(f, orgao)
    else:
        raise ValidationError('Formato ' + formato + ' inesperado')

    for contra_cheque in contra_cheques:
        validate_contra_cheque(contra_cheque)
        insert_file(contra_cheque,f)
        contra_cheque.save()


def register_matricula(f, orgao, formato):

    if formato == 'SAPITUR':
        matricula = read_matricula_sapitur(f)
    elif formato == 'CAMBUCI':
        matricula = read_matricula_cambuci(f)
    else:
        raise ValidationError('Formato ' + formato + ' inesperado')
    matricula.orgao = orgao

    try: # Caso a matrícula já exista esse metódo não retornará erro e como nada foi added retornarmos None
        Matricula.objects.matriculas_by_numero(matricula.numero, orgao)
        return None
    except:# Matrícula não existente, salva a nova matrícula e a retorna para ser added a lista
        matricula.save()
        return matricula

    else:
        raise ValidationError('Formato ' + formato + ' inesperado')


def validate_contra_cheque(contra_cheque):
    if contra_cheque.matricula_id is None:
        raise ValueError('Não foi possível localizar a matrícula neste arquivo. Verifique se este é um formato de contracheque válido')

    if contra_cheque.mes is None:
        raise ValueError('Não foi possível localizar o mês neste arquivo. Verifique se este é um formato de contracheque válido')

    if contra_cheque.exercicio is None:
        raise ValueError('Não foi possível localizar o exercício neste arquivo. Verifique se este é um formato de contracheque válido')



