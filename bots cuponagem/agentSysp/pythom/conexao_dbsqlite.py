import sqlite3

# Função para inicializar o banco SQLite
def init_db():
    conn = sqlite3.connect('coupons.db')  # Conecta ao banco SQLite (ou cria um novo arquivo)
    cursor = conn.cursor()

    # Cria a tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            codcli NUMBER,
            idcampanha NUMBER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ultimo_cupom INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def update_last_coupon(last_coupon):
    conn = sqlite3.connect('coupons.db')  # Conecta ao banco SQLite (ou cria um novo arquivo)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM processamento LIMIT 1")
    row = cursor.fetchone()
    
    if row:
        # Se já existir, faz o update da linha com o novo número do último cupom
        cursor.execute(f'''
            UPDATE processamento
            SET ultimo_cupom = {last_coupon}
            WHERE id = {row[0]}
        ''')
    else:
        # Caso contrário, insere uma nova linha
        cursor.execute(f'''
            INSERT INTO processamento (ultimo_cupom)
            VALUES ({last_coupon})
        ''')
    
    conn.commit()
    conn.close()

def get_last_coupon():
    conn = sqlite3.connect('coupons.db')  # Conecta ao banco SQLite (ou cria um novo arquivo)
    cursor = conn.cursor()

    cursor.execute("SELECT ultimo_cupom FROM processamento LIMIT 1")
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    if row:
        return row[0]
    else:
        return 0
        
# Função para salvar os cupons gerados no banco
def save_coupons_to_db(codcli, idcampanha):
    conn = sqlite3.connect('coupons.db')
    cursor = conn.cursor()

    # Insere os dados dos cupons gerados
    cursor.execute(f'''
        INSERT INTO coupons (timestamp, codcli, idcampanha)
        VALUES (DateTime('now'), {codcli}, {idcampanha})
    ''')

    conn.commit()
    conn.close()

# Função para obter a quantidade total de cupons gerados
def get_total_coupons_generated():
    conn = sqlite3.connect('coupons.db')
    cursor = conn.cursor()

    # Consulta para somar todos os cupons gerados
    cursor.execute(f'''
        SELECT SUM(timestamp) FROM coupons 
    ''')
    total_coupons = cursor.fetchone()[0]  # Pega o valor da soma

    conn.close()

    # Retorna 0 se o valor for None (nenhum cupom gerado ainda)
    return total_coupons if total_coupons is not None else 0