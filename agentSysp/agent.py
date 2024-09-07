import requests
import json
import time
import socket

# URL do servidor principal onde o agente enviará os dados
SERVER_URL = 'http://127.0.0.1:8000/reusables/agent_status/'  # Ajuste para a URL do seu servidor

# Função para obter o IP do servidor do banco de dados
def get_server_ip_from_db():
    # Aqui você deve implementar a lógica para se conectar ao seu banco de dados PostgreSQL
    # e buscar o IP do servidor. Para simplificação, usaremos um IP fixo.
    return 'http://127.0.0.1:8000/reusables/agent_status/'

# Função para enviar o status do agente para o servidor
def send_agent_status(coupons_generated):
    try:
        data = {
            'coupons_generated': coupons_generated,
            'agent_ip': socket.gethostbyname(socket.gethostname()),  # IP do agente
            'name': socket.gethostname(), 
        }
        response = requests.post(SERVER_URL, json=data)
        print(f'Status enviado. Código de resposta: {response.status_code}')
    except Exception as e:
        print(f'Erro ao enviar status: {e}')

# Simulação do agente
def main():
    while True:
        coupons_generated = 10  # Exemplo de número de cupons gerados

        send_agent_status( coupons_generated)

        # Espera por um intervalo antes de enviar o próximo status
        time.sleep(60)  # A cada 60 segundos

if __name__ == '__main__':
    main()
