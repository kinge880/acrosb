import sys
import os
import socket
from instanciapastas import instantclient_dir

import cx_Oracle

# Inicializar o cliente Oracle com o caminho do instantclient
try:
    cx_Oracle.init_oracle_client(lib_dir=instantclient_dir)
    print("Oracle Client initialized successfully")
except cx_Oracle.DatabaseError as e:
    print("Error:", e)

def createConnection():
    host=socket.gethostbyname(socket.gethostname())
    #host='172.16.22.110'

    print('instancia a conexão')
    conexao = cx_Oracle.connect(f"CAIXA/CAIXA@{host}/XE")
    
    return conexao