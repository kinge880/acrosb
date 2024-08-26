from django import forms
from .models import PresentationSettings

class PresentationSettingsForm(forms.ModelForm):
    class Meta:
        model = PresentationSettings
        fields = [
                    'idempresa',
                    'background_type',
                    'background_color', 
                    'background_url', 
                    'filter_color', 
                    'initial_text', 
                    'logo_type', 
                    'logo_text', 
                    'logo_image'
                ]