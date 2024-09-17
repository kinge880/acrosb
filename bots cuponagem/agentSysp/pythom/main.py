import psutil
import socket
import requests
from conexao_dbsqlite import *
from cuponagem import *
from criarcupom import *
from datetime import datetime
import pytz
import os
from instanciapastas import imprimir_cupom

# URL do servidor principal onde o agente enviará os dados
SERVER_URL = 'http://172.16.21.145:8000/'
service_version = '0.112092024'
restart = datetime.now().isoformat()
local_timezone = pytz.timezone('America/Sao_Paulo')
        
# Função para obter informações do sistema
def get_system_info():
    # Uso da CPU em porcentagem
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Memória usada em MB
    memory_info = psutil.virtual_memory()
    memory_used = memory_info.used / (1024 ** 2)  # Converter para MB
    
    # Calcular uptime a partir da data de reinício
    restart_time = datetime.fromisoformat(restart).astimezone(local_timezone)
    current_time = datetime.now(local_timezone)
    uptime = (current_time - restart_time).total_seconds()
    
    return {
        'cpu_usage': cpu_usage,
        'memory_used': memory_used,
        'uptime': uptime
    }

# Função para enviar o status do agente para o servidor
def send_agent_status():
    system_info = get_system_info()
    coupons_generated = get_total_coupons_generated()
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
    init_db() 
    
    while True:
        # Envia status do agente para o servidor
        send_agent_status()
        numpedecf = pegaUltimaVenda()            
        ultnumped = get_last_coupon()
        print(numpedecf)
        print(ultnumped)
        if ultnumped != numpedecf[0]:
            ped = processacupom(numpedecf[0])
            
            if ped:
                update_last_coupon(numpedecf[0])
                
                conexao_postgre = conectar_banco()
                cursor_postgre = conexao_postgre.cursor()
                
                if ped and len(ped) > 0:
                    for i in range(ped[11]):
                        criar_cupom(
                            ped[3], ped[0],  numpedecf[2],  numpedecf[3], numpedecf[3], '68 99207-0446',
                            ped[2], ped[3], ped[5], ped[6], ped[10]
                        )
                        
                        imprimir_cupom(ped[0])
                        
                        # Inserção em cpfcli_cuponagem
                        cursor_postgre.execute(f'''
                            INSERT INTO cpfcli_cuponagem
                            (
                                id, dtmov, numpedecf, valor, codcli, nomecli, emailcli, telcli, cpf_cnpj, 
                                dataped, bonificado, ativo, idcampanha, tipo, numcaixa
                            )
                            VALUES (
                                DEFAULT, 
                                NOW(), 
                                {ped[0]},  -- Número do pedido
                                {ped[1]},  -- Valor total
                                {ped[2]},  -- Código do cliente
                                '{ped[3]}', -- nomecli
                                '{ped[4]}', --email
                                '{ped[5]}', --tell
                                '{ped[6]}', --cpf_cnpj
                                '{ped[7]}', -- Data do pedido
                                '{ped[8]}', -- Bonificado (ajustar conforme necessário)
                                'S', -- Ativo
                                {ped[9]}, -- ID da campanha
                                'CC',
                                {numpedecf[1]}
                            )
                        ''')
                        
                        conexao_postgre.commit()
                else:
                    print('venda não gerou cupom!')
            
                conexao_postgre.close()
        else:
            print('nenhuma nova venda!')
        
        # Espera por um intervalo antes de enviar o próximo status
        time.sleep(1) 

if __name__ == '__main__':
    main()
