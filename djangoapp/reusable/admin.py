from django.contrib import admin
from .models import AccessLog

class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip_address', 'user', 'path', 'method', 'action_type')
    list_filter = ('timestamp', 'user', 'action_type')
    search_fields = ('ip_address', 'path', 'user__username', 'request_body')

admin.site.register(AccessLog, AccessLogAdmin)