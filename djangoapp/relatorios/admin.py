from django.contrib import admin
from django.utils import timezone
from .models import Report

class RelatorioAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de objetos
    list_display = ('descricao', 'dtmov', 'categoria')
    
    # Filtros para ajudar a localizar registros
    list_filter = ('categoria', 'dtmov')
    
    # Campos que podem ser pesquisados
    search_fields = ('descricao', 'categoria')
    
    # Ordenação padrão dos registros
    ordering = ('-dtmov',)  # Ordena por data do movimento de forma decrescente
    
    # Campos do formulário organizados em seções
    fieldsets = (
        (None, {
            'fields': ('descricao', 'categoria')
        }),
    )
    
    # Descrição customizada para o formulário de edição
    def get_form_description(self, request, obj=None):
        if obj:
            return f'Edição do relatório: {obj.descricao}'
        else:
            return 'Adicionar novo relatório'

    # Adiciona um filtro de datas para o campo de data do movimento
    date_hierarchy = 'dtmov'

    def save_model(self, request, obj, form, change):
        if not obj.dtmov:  # Se 'dtmov' não estiver definido
            obj.dtmov = timezone.now()  # Define a data e hora atual
        super().save_model(request, obj, form, change)  # Salva o modelo

# Registra o ModelAdmin
admin.site.register(Report, RelatorioAdmin)