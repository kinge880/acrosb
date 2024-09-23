from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

from django import template

register = template.Library()

@register.filter(name='add_class_invalid')
def add_class_invalid(field):
    # Obtém as classes existentes
    existing_classes = field.field.widget.attrs.get('class', '')
    
    # Adiciona a classe 'is-invalid' se houver erros
    if field.errors:
        new_classes = f"{existing_classes} is-invalid".strip()
    else:
        new_classes = existing_classes
    
    return field.as_widget(attrs={"class": new_classes})
