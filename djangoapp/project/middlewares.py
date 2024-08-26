from django.utils.deprecation import MiddlewareMixin
from acounts.models import PresentationSettings, Profile, empresa

class CustomCSSMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Adicionar a lógica para obter e armazenar as variáveis do CSS
        request.custom_css_vars = self._get_custom_css_vars(request)

    def _get_custom_css_vars(self, request):
        # Obtém o primeiro objeto ou um objeto vazio
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            idempres = empresa.objects.get(id=profile.idempresa.id)
            settings = PresentationSettings.objects.filter(idempresa=idempres).first()  # Obtém o primeiro objeto ou None
        
            if settings is None:
                # Se não encontrar nenhum objeto, cria um objeto vazio
                settings = PresentationSettings()
            
            return {
                'background_type': settings.background_type or '',
                'background_color': settings.background_color or '',
                'background_url': settings.background_url or '',
                'filter_color': settings.filter_color or '',
                'initial_text': settings.initial_text or '',
                'logo_type': settings.logo_type or '',
                'logo_text': settings.logo_text or '',
                'logo_image': settings.logo_image or '',
            }
