from django.contrib import admin
from django.contrib.auth.models import User
from .models import *  # Ensure this matches the class name
from django.contrib.auth.admin import UserAdmin

class EmpresaAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de objetos
    list_display = ('empresa', 'dtcadastro', 'ativo', 'modulo_cliente')
    
    # Adiciona filtros na lateral para facilitar a busca
    list_filter = ('ativo','modulo_cliente')
    
    # Adiciona uma barra de pesquisa para pesquisar por nome da empresa
    search_fields = ('empresa','modulo_cliente')
    
    # Adiciona um campo para ordenação
    ordering = ('-dtcadastro','modulo_cliente')  # Ordena por data de cadastro de forma decrescente
    
    # Ordena os campos do formulário de edição
    fieldsets = (
        (None, {
            'fields': ('empresa', 'ativo','modulo_cliente', 'dtcadastro')
        }),
    )
    
    # Adiciona um filtro de datas para o campo de cadastro
    date_hierarchy = 'dtcadastro'
    
    # Adiciona um filtro por status de ativo
    list_filter = ('ativo',)

    # Personaliza o título do formulário
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    # Adiciona um título customizado ao formulário de edição
    def get_form_description(self, request, obj=None):
        if obj:
            return f'Edição da empresa: {obj.empresa}'
        else:
            return 'Adicionar nova empresa'

# Registra o ModelAdmin
admin.site.register(empresa, EmpresaAdmin)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'
    extra = 0
    fields = ('idempresa',)  # Adicione outros campos se necessário

class Userad(UserAdmin):
    inlines = [ProfileInline]

# Substitui o UserAdmin padrão para incluir o ProfileInline
admin.site.unregister(User)
admin.site.register(User, Userad)

class PresentationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'idempresa', 'background_type', 'background_color', 'background_url',
        'background_type_mobile', 'background_url_mobile', 'background_color_mobile',
        'filter_color', 'filter_color_mobile', 'initial_text', 'logo_type',
        'logo_text', 'logo_image', 'client_title', 'client_subtitle',
        'client_background_type', 'client_background_color', 'client_background_url',
        'client_background_type_mobile', 'client_background_url_mobile', 'client_background_color_mobile',
        'client_filter_color', 'client_filter_color_mobile'
    )
    list_filter = ('background_type', 'logo_type', 'client_background_type')
    search_fields = ('idempresa', 'initial_text', 'logo_text', 'client_title', 'client_subtitle')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object exists (i.e., we are editing)
            return ['idempresa']  # Make the idempresa field read-only
        else:
            return []
    
    def get_field_queryset(self, db, request, model, field_name):
        if field_name == 'idempresa':
            return model.objects.filter(idempresa=request.user.id)
        return super().get_field_queryset(db, request, model, field_name)

admin.site.register(PresentationSettings, PresentationSettingsAdmin)