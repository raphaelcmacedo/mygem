import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from my-gem.core.connectors.pdf import pdf_to_txt_pypdf
from my-gem.core.models import Matricula
from my-gem.core.util import mes_string_to_int

REGEX_CPF = r'(^[0-9]{3}[\.][0-9]{3}[\.][0-9]{3}[-][0-9]{2})'

def read_informe_rendimento(f, orgao):
    lines = pdf_to_txt_pypdf(f)
    contra_cheques = []
    from my-gem.core.models import ContraCheque

    matriculas = []
    exercicio = ''

    for i, line in enumerate(lines):
        if matriculas and exercicio:
            break

        cpf_search = re.search(REGEX_CPF, line)
        if cpf_search:
            cpf = cpf_search.group(0).replace('.', '').replace('-', '')

            matriculas = Matricula.objects.matriculas_by_cpf(cpf)
            if not matriculas:
                raise ValueError('Usuário {} não cadastrado'.format(cpf))

            continue

        if 'Ano-calendário de' in line:  # Verifica se achou ano e mês baseado na regra MM / aaaa
            exercicio = line.split(' ')[-1]

    for matricula in matriculas:
        contra_cheque = ContraCheque()
        contra_cheque.matricula = matricula
        contra_cheque.mes = 0
        contra_cheque.exercicio = exercicio
        contra_cheques.append(contra_cheque)

    return contra_cheques


