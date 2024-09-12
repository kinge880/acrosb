import psutil
import socket
import requests
import json
import time
from datetime import datetime
import pytz

# URL do servidor principal onde o agente enviará os dados
SERVER_URL = 'http://127.0.0.1:8000/'
service_version = '0.112092024'
restart = datetime.now().isoformat()

# Função para obter informações do sistema
def get_system_info():
    # Uso da CPU em porcentagem
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Memória usada em MB
    memory_info = psutil.virtual_memory()
    memory_used = memory_info.used / (1024 ** 2)  # Converter para MB
    
    # Calcular uptime a partir da data de reinício
    local_timezone = pytz.timezone('America/Sao_Paulo')
    restart_time = datetime.fromisoformat(restart).astimezone(local_timezone)
    current_time = datetime.now(local_timezone)
    uptime = (current_time - restart_time).total_seconds()
    
    return {
        'cpu_usage': cpu_usage,
        'memory_used': memory_used,
        'uptime': uptime
    }
    
# Função para obter o horário atual ajustado para o fuso horário local
def get_local_time():
    local_timezone = pytz.timezone('America/Sao_Paulo')  # Substitua pelo fuso horário desejado
    local_time = datetime.now(local_timezone).isoformat()
    return local_time

# Função para enviar o status do agente para o servidor
def send_agent_status(coupons_generated):
    system_info = get_system_info()
    data = {
        'coupons_generated': coupons_generated,
        'agent_ip': socket.gethostbyname(socket.gethostname()),  # IP do agente
        'name': socket.gethostname(),  # Nome do host
        'cpu_usage': system_info['cpu_usage'],  # Uso da CPU
        'memory_used': system_info['memory_used'],
        'uptime': system_info['uptime'],  # Tempo de atividade
        'service_version': service_version,
        'last_restart': restart
    }
    response = requests.post(SERVER_URL+'reusables/agent_status/', json=data)
    print(f'Status enviado para {SERVER_URL+'reusables/agent_status/'}. Código de resposta: {response.status_code}')

# Simulação do agente
def main():
    while True:
        coupons_generated = 10  # Exemplo de número de cupons gerados

        send_agent_status( coupons_generated)

        # Espera por um intervalo antes de enviar o próximo status
        time.sleep(1) 

if __name__ == '__main__':
    main()
