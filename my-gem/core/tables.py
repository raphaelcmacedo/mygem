import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A
from django.contrib.auth.models import User


class UserTable(tables.Table):
    editar = tables.LinkColumn('edit_user', args=[A('id')], orderable=False, text=mark_safe('<i class="fa fa-pencil" aria-hidden="true"></i>'))
    senha = tables.LinkColumn('change_password', args=[A('id')], orderable=False,text=mark_safe('<i class="fa fa-key" aria-hidden="true"></i>'))

    class Meta:
        model = User
        orderable = False
        fields = ('username', 'email', 'first_name', 'last_name')
        attrs = {"class": "paleblue"}
        sequence = ('editar', 'senha','username', 'email', 'first_name', 'last_name')

