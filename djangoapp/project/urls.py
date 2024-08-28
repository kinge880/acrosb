from baton.autodiscover import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include("cpfcli.urls")),
    path('accounts/', include("acounts.urls")),
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('reusables/', include("reusable.urls")),
    path('relatorios/', include("relatorios.urls")),
]  

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
    )