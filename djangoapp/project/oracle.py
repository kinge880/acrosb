import cx_Oracle
import os

# Diretório onde você copiou o Instant Client no Docker
diretorio_c = '/usr/lib/instantclient'

# Caminho completo da pasta
caminho_pasta = os.path.join(diretorio_c)

# Inicializa o cliente Oracle
try:
    cx_Oracle.init_oracle_client(lib_dir=caminho_pasta)
    print("Oracle Client Initialized Successfully")
except Exception as e:
    print(f"Error initializing Oracle Client: {e}")

def conexao_oracle():
    conexao = cx_Oracle.connect(user="LGBRASIL", password="LS16BR", dsn="172.16.23.20/wint")
    return conexao