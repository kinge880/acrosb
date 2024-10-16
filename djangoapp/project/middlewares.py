from django.utils.deprecation import MiddlewareMixin
from acounts.models import PresentationSettings, Profile, empresa
from reusable.models import AccessLog
import json
from django.utils import timezone

class CustomCSSMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Adicionar a lógica para obter e armazenar as variáveis do CSS
        request.custom_css_vars = self._get_custom_css_vars(request)

    def _get_custom_css_vars(self, request):
        # Obtém o primeiro objeto ou um objeto vazio
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            idempres = empresa.objects.get(id=profile.idempresa.id)
            settings = PresentationSettings.objects.filter(idempresa=1).first()  # Obtém o primeiro objeto ou None
        
            if settings is None:
                # Se não encontrar nenhum objeto, cria um objeto vazio
                settings = PresentationSettings()
            
            return {
                'background_type': settings.background_type or '',
                'background_color': settings.background_color or '',
                'background_url': settings.background_url or '',
                'filter_color': settings.filter_color or '',
                'background_type_mobile': settings.background_type_mobile or '',
                'background_color_mobile': settings.background_color_mobile or '',
                'background_url_mobile': settings.background_url_mobile or '',
                'filter_color_mobile': settings.filter_color_mobile or '',
                'initial_text': settings.initial_text or '',
                'logo_type': settings.logo_type or '',
                'logo_text': settings.logo_text or '',
                'logo_image': settings.logo_image or '',
                'logo_type_mobile': settings.logo_type_mobile or '',
                'logo_text_mobile': settings.logo_text_mobile or '',
                'logo_image_mobile': settings.logo_image_mobile or '',
                'client_title' : settings.client_title or '',
                'client_subtitle' : settings.client_subtitle or '',
                'error_message_suport' : settings.error_message_suport or '',
            }
        else:
            settings = PresentationSettings.objects.filter(idempresa=1).first()  # Obtém o primeiro objeto ou None
        
            if settings is None:
                # Se não encontrar nenhum objeto, cria um objeto vazio
                settings = PresentationSettings()
            
            return {
                'background_type': settings.background_type or '',
                'background_color': settings.background_color or '',
                'background_url': settings.background_url or '',
                'filter_color': settings.filter_color or '',
                'background_type_mobile': settings.background_type_mobile or '',
                'background_color_mobile': settings.background_color_mobile or '',
                'background_url_mobile': settings.background_url_mobile or '',
                'filter_color_mobile': settings.filter_color_mobile or '',
                'initial_text': settings.initial_text or '',
                'logo_type': settings.logo_type or '',
                'logo_text': settings.logo_text or '',
                'logo_image': settings.logo_image or '',
                'logo_type_mobile': settings.logo_type_mobile or '',
                'logo_text_mobile': settings.logo_text_mobile or '',
                'logo_image_mobile': settings.logo_image_mobile or '',
                'client_title' : settings.client_title or '',
                'client_subtitle' : settings.client_subtitle or '',
                'error_message_suport' : settings.error_message_suport or '',
            }
            
def is_valid_ip(ip):
    """
    Valida se um IP é do formato correto (IPv4 ou IPv6).
    """
    import re
    ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    ipv6_pattern = re.compile(r'^([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{1,4}$')
    
    return ipv4_pattern.match(ip) or ipv6_pattern.match(ip)
        
def get_client_ip(request):
    """
    Obtém o IP real do cliente, considerando diferentes cabeçalhos que podem
    ser configurados por proxies e balanceadores de carga.
    """
    # Tenta obter o IP do cabeçalho X-Forwarded-For
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # O valor pode ser uma lista de IPs, então o primeiro é o IP real do cliente
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Tenta obter o IP do cabeçalho X-Real-IP
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            ip = x_real_ip.strip()
        else:
            # Se não há X-Forwarded-For nem X-Real-IP, usa o REMOTE_ADDR
            ip = request.META.get('REMOTE_ADDR')
    
    # Se o IP não estiver no formato correto, pode ser uma tentativa de manipulação
    if not ip or not is_valid_ip(ip):
        ip = 'IP inválido ou não disponível'
    
    return ip

class AccessLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/static/') or  request.path.startswith('/media/') or request.path.startswith('/baton/') or request.path.startswith('/reusables/') or request.path.startswith('/admin/') or request.path.startswith('/admin_tools_stats/') or request.path.startswith('/admin_tools_stats/'):
            return
        # Apenas logar requisições GET e POST
        if request.method in ['GET', 'POST']:
            ip_address = get_client_ip(request)
            user = request.user if request.user.is_authenticated else None
            path = request.get_full_path()
            method = request.method
            action_type = method  # Usamos o método HTTP como tipo de ação

            # Obter o corpo da requisição para POST (em formato JSON, se possível)
            request_body = ''
            if method == 'POST':
                try:
                    request_body = json.dumps(request.POST.dict())
                except Exception as e:
                    request_body = str(e)

            # Criar e salvar o log
            AccessLog.objects.create(
                ip_address=ip_address,
                user=user,
                path=path,
                method=method,
                action_type=action_type,
                request_body=request_body
            )
