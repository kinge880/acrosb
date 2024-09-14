import psycopg2
import os

# Conexão com o banco de dados
def conectar_banco():
    return psycopg2.connect(
        dbname="acrosbd",
        user="acrosbookuser",
        password="acrsdosbodkuser23457645f",
        host="localhost",
        port="54320"
    )
