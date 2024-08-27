from django.shortcuts import render
from .models import Report

# Create your views here.
def menu(request):
    reports = Report.objects.all()
    context = {
        'title': 'Lista de Relatórios',
        'reports': reports
    }
    return render(request, 'menu.html', context)