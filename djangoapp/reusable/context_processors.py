from project.middlewares import CustomCSSMiddleware

def css_vars_processor(request):
    # Instanciar o middleware para acessar o método _get_custom_css_vars
    middleware = CustomCSSMiddleware(lambda req: None)
    css_vars = middleware._get_custom_css_vars(request)
    return {'variaveis_globais': css_vars}