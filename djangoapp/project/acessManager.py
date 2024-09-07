

from .conexao_postgresql import *
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def get_permissions(model, app_name):
    content_type = ContentType.objects.get_for_model(model)

    # Obtendo todas as permissões relacionadas ao ContentType
    all_permission = Permission.objects.filter(content_type=content_type)
    
    permissao_view = [item.codename for item in all_permission if 'view' in item.codename]
    if permissao_view and len(permissao_view) > 0:
        permissao_view = permissao_view[0]
    else:
        permissao_view = 'NA'

    permissao_add = [item.codename for item in all_permission if 'add' in item.codename]
    if permissao_add and len(permissao_add) > 0:
        permissao_add = permissao_add[0]
    else:
        permissao_add = 'NA'

    permissao_change= [item.codename for item in all_permission if 'change' in item.codename]
    if permissao_change and len(permissao_change) > 0:
        permissao_change = permissao_change[0]
    else:
        permissao_change = 'NA'

    permissao_delete = [item.codename for item in all_permission if 'delete' in item.codename]
    if permissao_delete and len(permissao_delete) > 0:
        permissao_delete = permissao_delete[0]
    else:
        permissao_delete = 'NA'
    
    return {'view': str(app_name)+'.'+str(permissao_view), 
            'add': str(app_name)+'.'+str(permissao_add), 
            'change': str(app_name)+'.'+str(permissao_change), 
            'delete': str(app_name)+'.'+str(permissao_delete)}