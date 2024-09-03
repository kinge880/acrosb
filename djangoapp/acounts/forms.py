from django import forms
from .models import PresentationSettings
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class PresentationSettingsForm(forms.ModelForm):
    class Meta:
        model = PresentationSettings
        fields = [
                    'idempresa',
                    'background_type',
                    'background_color', 
                    'background_url', 
                    'filter_color', 
                    'background_type_mobile',
                    'background_color_mobile', 
                    'background_url_mobile', 
                    'filter_color_mobile', 
                    'initial_text', 
                    'logo_type', 
                    'logo_text', 
                    'logo_image',
                    'logo_type_mobile', 
                    'logo_text_mobile', 
                    'logo_image_mobile'
                ]
