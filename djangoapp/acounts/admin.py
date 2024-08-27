from django.contrib import admin
from django.contrib.auth.models import User
from .models import *  # Ensure this matches the class name

class EmpresaAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de objetos
    list_display = ('empresa', 'dtcadastro', 'ativo')
    
    # Adiciona filtros na lateral para facilitar a busca
    list_filter = ('ativo',)
    
    # Adiciona uma barra de pesquisa para pesquisar por nome da empresa
    search_fields = ('empresa',)
    
    # Adiciona um campo para ordenação
    ordering = ('-dtcadastro',)  # Ordena por data de cadastro de forma decrescente
    
    # Ordena os campos do formulário de edição
    fieldsets = (
        (None, {
            'fields': ('empresa', 'ativo')
        }),
        ('Informações adicionais', {
            'classes': ('collapse',),
            'fields': ('dtcadastro',)
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

class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]
    
    # Campos a serem exibidos na lista de objetos
    list_display = ('username', 'email', 'first_name', 'last_name')
    
    # Campos que podem ser pesquisados
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Ordenação padrão dos registros
    ordering = ('username',)
    
    # Campos do formulário de edição
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Informações pessoais', {
            'fields': ('first_name', 'last_name')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    
    # Exclui campos não editáveis diretamente
    readonly_fields = ('password',)

# Substitui o UserAdmin padrão para incluir o ProfileInline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)