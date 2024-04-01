import psycopg2
import os

# Conexão com o banco de dados
def conectar_banco():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'change-me'),
        user=os.getenv('POSTGRES_USER', 'change-me'),
        password=os.getenv('POSTGRES_PASSWORD', 'change-me'),
        host=os.getenv('POSTGRES_HOST', 'change-me'),
        port=os.getenv('POSTGRES_PORT', 'change-me')
    )
