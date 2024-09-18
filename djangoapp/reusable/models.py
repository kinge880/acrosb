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
    
class Agent(models.Model):
    name = models.CharField(max_length=500, unique = True)
    agent_ip = models.CharField(max_length=100)
    numcaixa = models.IntegerField(null=True, blank=True)
    codfilial = models.IntegerField(null=True, blank=True)
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    uptime = models.DurationField(null=True, blank=True)
    service_version = models.CharField(max_length=100, null=True, blank=True)
    last_restart = models.DateTimeField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(auto_now=True)

class AgentDesactive(models.Model):
    numcaixa = models.IntegerField(null=True, blank=True)
    dtmov = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.numcaixa} - {self.dtmov}'