from django.shortcuts import render
import json
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login as loginDjango
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings
from django.db.models import Q
from project.conexao_postgresql import *
import io 
from datetime import datetime
import numpy as np
from django.contrib.auth.hashers import check_password, make_password
import re

#Anonymous required 
def anonymous_required(function=None, redirect_url='/'):

    if not redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator

def logout_view(request):
    logout(request)

    return redirect('/')

#controles de login e cadastro de usuário
@anonymous_required
def login(request):
    
    if request.method == 'POST' :
        usuario = request.POST.get("username")
        senha = request.POST.get("password")
        
        user = authenticate(username=usuario, password=senha)

        if user:
            loginDjango(request, user)
            return redirect('/')
        else:
            messages.error(request, f'Nome de usuário ou senha incorretos!')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html', {'login': 'login'})