import sys
import os
cupons_dir = 'Cupons'
instantclient_dir = 'instantclient_18_5'

if getattr(sys, 'frozen', False):
    instaclient_dir = os.path.join(sys._MEIPASS, instantclient_dir)
    # Add Oracle Client library directory to PATH
    os.environ['PATH'] = instantclient_dir + os.path.pathsep + os.environ['PATH']

if getattr(sys, 'frozen', False):
    cupons_dir = os.path.join(sys._MEIPASS, cupons_dir)
    # Add Oracle Client library directory to PATH
    os.environ['PATH'] = cupons_dir + os.path.pathsep + os.environ['PATH']

# Verificar se a pasta 'Cupons' existe, se não, cria a pasta
if not os.path.exists(cupons_dir):
    os.makedirs(cupons_dir)

# Função para gerar o caminho do arquivo dentro da pasta 'Cupons'
def caminho_arquivo_cupom(i):
    return os.path.join(cupons_dir, f"Cupom_{i}.txt")

# Exemplo de como abrir e imprimir o arquivo
def imprimir_cupom(i):
    caminho_cupom = caminho_arquivo_cupom(i)
    if os.path.exists(caminho_cupom):
        os.startfile(caminho_cupom, "print")
    else:
        print(f"O arquivo {caminho_cupom} não existe.")