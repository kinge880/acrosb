from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class AccessLog(models.Model):
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.TextField()
    method = models.CharField(max_length=10)
    action_type = models.CharField(max_length=20)  # Pode ser 'GET', 'POST', etc.
    request_body = models.TextField(blank=True, null=True)  # Armazena o corpo da requisição, se aplicável

    def __str__(self):
        return f"{self.timestamp} - {self.ip_address} - {self.path} - {self.action_type}"