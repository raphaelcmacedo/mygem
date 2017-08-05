import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from my-gem.core.connectors.pdf import convert_pdf_to_txt
from my-gem.core.models import Matricula
from my-gem.core.util import mes_string_to_int

REGEX_MATRICULA_SAPITUR = r'^\d+\s+\w+\s+\w+'

def read_contra_cheque_sapitur(f, matriculas_dict):
    lines = convert_pdf_to_txt(f)

    from my-gem.core.models import ContraCheque
    contra_cheque = ContraCheque()

    for i, line in enumerate(lines):
        if re.search(REGEX_MATRICULA_SAPITUR, line):
            key = line.split(' ')[0]
            try:
                contra_cheque.matricula = matriculas_dict[key]
            except:
                raise ValueError('Matrícula {} não cadastrada'.format(key))

            continue

        if ' / ' in line:  # Verifica se achou ano e mês baseado na regra MM / aaaa
            mesAno = line.split('/')
            contra_cheque.mes = mes_string_to_int(mesAno[0].strip())
            contra_cheque.exercicio = mesAno[1].strip()

    return contra_cheque

def read_matricula_sapitur(f):
    lines = convert_pdf_to_txt(f)

    matricula = Matricula()

    # Busca o número da matrícula

    for i, line in enumerate(lines):

        if re.search(REGEX_MATRICULA_SAPITUR, line):
            parts = line.split(' ')
            matricula.numero = ''
            nome = ''
            sobrenome = ''
            for part in parts:
                if len(part) > 0:#part possui valor
                    if len(matricula.numero) <= 0:
                        matricula.numero = part
                    elif len(nome) <= 0:
                        nome = part.title()
                    else:
                        sobrenome = sobrenome + ' ' + part.title()
            sobrenome = sobrenome.strip()[:30]


    # Busca o cpf pelo nome do arquivo
    try:
        filename = f['name']
    except:
        filename = str(f)
    index = filename.index('-')
    cpf = filename[:index].strip()

    # Verifica se esse cpf já possui um usuário caso contrário cadastra
    try:
        user = User.objects.get(username=cpf)
    except ObjectDoesNotExist:
        user = User()
        user.username = cpf
        user.password = make_password(matricula.numero)
        user.first_name = nome
        user.last_name = sobrenome
        user.save()
    matricula.user = user


    return matricula

