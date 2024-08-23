from oracle import *
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import datetime 
from DateFormat import dateFormat

'ALTER TABLE PCPEDC ADD EMITECUPOM VARCHAR2(1) NULL;'

#envio de email
# Configurações do servidor SMTP
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "deeptrackemails@gmail.com"
smtp_password = "egqpqsoxbacwulkl"

# Função que envia o e-mail
def enviaremail(qtnumeros, nome, email, qtcupons_total, numcupom):

    if email:
        # Configuração da mensagem
        print(f'iniciando envio do email para {email}')
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = f'Parabéns {nome} você está concorrendo a um prêmio!'
        
        # Corpo do e-mail
        corpo_email = f"""
        Olá {nome},
        
        Gostaríamos de informar que você recebeu {qtnumeros} números da sorte após sua compra no cupom {numcupom} e está concorrendo a um prêmio incrível!
        Atualmente seu cadastro possui {qtcupons_total[0]} números da sorte acumulados, boa sorte!
        """
        print('adicionando mensagem ao email')
        msg.attach(MIMEText(corpo_email, 'plain'))
        
        print('conectando ao SMTP')
        # Iniciar conexão com o servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        print('enviando')
        # Enviar e-mail
        server.sendmail(smtp_username, email, msg.as_string())
        print('encerrando')
        # Encerrar conexão
        server.quit()

def processacupom():
    print('iniciando...')
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    cursor.execute(f'''
        SELECT
            IDCAMPANHA, DESCRICAO, USAFORNEC, USAPROD, VALOR,
             MULTIPLICADOR, to_char(DTINIT, 'yyyy-mm-dd'), 
             to_char(DTFIM, 'yyyy-mm-dd'), ENVIAEMAIL, TIPOINTENSIFICADOR, FORNECVALOR, PRODVALOR
        FROM MSCUPONAGEMCAMPANHA
        WHERE 
            ATIVO = 'S'
    ''')
    campanha = cursor.fetchone()

    if campanha is None:
        return 'Não existe campanha ativa'

    #parametros
    idcampanha = campanha[0]
    usa_fornec = campanha[2]
    usa_prod = campanha[3]
    valor = campanha[4]
    multiplicador_cupom = campanha[5]
    dt_inicial = campanha[6]
    dt_final = campanha[7]
    envia_email = campanha[8]
    tipo_intensificador = campanha[9]
    valor_fornecedor = campanha[10]
    valor_prod = campanha[11]
    testa_envio_email = True
    listprodsWhere = ',NULL'
    produtoFornecWhere = ',NULL'

    #parametros de produto
    if usa_prod and usa_prod == 'C':
        cursor.execute(f'''
            SELECT codprod FROM MSCUPONAGEMPROD WHERE IDCAMPANHA = {idcampanha}
        ''')
        produtos = cursor.fetchall()

        listaprods = []
        for item in produtos:
            listaprods.extend(item)
        listaprods = tuple(listaprods)

        if len(listaprods) > 0:
            listprodsWhere = f',(SELECT NUMPED FROM PCPEDI WHERE CODPROD IN {listaprods} AND NUMPED = PCPEDC.NUMPED AND ROWNUM = 1) AS LISTPROD'
    
    elif usa_prod and usa_prod == 'M':
        listprodsWhere = f',(SELECT COUNT(DISTINCT CODPROD) FROM PCPEDI WHERE NUMPED = PCPEDC.NUMPED) AS LISTPROD'
    
    #parametros de fornecedor  
    if usa_fornec and usa_fornec == 'C':
        cursor.execute(f'''
            SELECT codprod FROM MSCUPONAGEMPROD WHERE IDCAMPANHA = {idcampanha}
        ''')
        fornecedores = cursor.fetchall()

        listfornecs = []
        for item in fornecedores:
            listfornecs.extend(item)
        listfornecs = tuple(listfornecs)

        if len(listfornecs) > 0:
            produtoFornecWhere = f',(SELECT NUMPED FROM PCPEDI WHERE CODPROD IN {listfornecs} AND NUMPED = PCPEDC.NUMPED AND ROWNUM = 1) AS LISTFORNEC'
    
    elif usa_prod and usa_prod == 'M':
        produtoFornecWhere = f',(SELECT COUNT(DISTINCT CODFORNEC) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDI WHERE NUMPED = PCPEDC.NUMPED)) AS LISTPROD'
    
    print('iniciando pesquisa de pedidos...')

    cursor.execute(f'''
        SELECT 
            NUMPED, 
            VLTOTAL,
            TO_CHAR("DATA", 'yyyy-mm-dd'), 
            CODCLI,
            (SELECT CLIENTE FROM PCCLIENT WHERE CODCLI = PCPEDC.CODCLI ),
            (SELECT EMAIL FROM PCCLIENT WHERE CODCLI = PCPEDC.CODCLI)
            {produtoFornecWhere}
            {listprodsWhere}
        FROM PCPEDC 
        WHERE 
            "DATA" BETWEEN to_date('{dt_inicial}', 'yyyy-mm-dd') AND to_date('{dt_final}', 'yyyy-mm-dd') AND
            POSICAO = 'F' AND 
            ORIGEMPED IN ('F', 'T', 'R', 'B', 'A') AND 
            CONDVENDA != 10 AND
            NOT EXISTS (
                SELECT 1
                FROM MSCUPONAGEM
                WHERE MSCUPONAGEM.NUMPED = PCPEDC.NUMPED
            ) AND 
            CODCLI > 1 AND 
            PCPEDC.VLTOTAL >= {valor} 
    ''')
    pedidos = cursor.fetchall()

    print('pedidos pesquisados, calculando numeros da sorte')
    cont = 1

    for ped in pedidos:
        print(f'processando pedido {ped} posição {cont} de {len(pedidos)}')
        import math

        qtcupons = int(math.floor(ped[1] / valor))

        if ped[6] is not None or ped[7] is not None:
            bonificadoWhere = 'S'
            
            if tipo_intensificador == 'M':
                qtcupons = qtcupons * multiplicador_cupom
            elif tipo_intensificador == 'S':
                if ped[6] and ped[6] > valor_fornecedor:
                    qtcupons = qtcupons + multiplicador_cupom
                if ped[6] and ped[6] > valor_fornecedor:
                    qtcupons = qtcupons + multiplicador_cupom
            else:
                bonificadoWhere = 'N'
        else:
            bonificadoWhere = 'N'
        
        if qtcupons >= 1:
            for i in range(qtcupons):
                print(f'''gerando numero da sorte pedido {ped[0]} volume {i + 1} de {qtcupons}''')
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEM
                    (ID, DATAPED, DTMOV, NUMPED, VALOR, BONIFICADO, NUMSORTE, CODCLI, IDCAMPANHA)
                    VALUES((SELECT COALESCE(MAX(id), 0) + 1 FROM MSCUPONAGEM), TO_DATE('{ped[2]}', 'yyyy-mm-dd'), SYSDATE, {ped[0]}, {ped[1]}, 
                    '{bonificadoWhere}', (SELECT COALESCE(MAX(NUMSORTE), 0) + 1 FROM MSCUPONAGEM WHERE IDCAMPANHA = {idcampanha}), {ped[3]}, {idcampanha})
                ''')
            
            cursor.execute(f'''
                SELECT count(DISTINCT numsorte) FROM MSCUPONAGEM WHERE CODCLI = {ped[3]}
            ''')
            qtcupons_total = cursor.fetchone()
            
            conexao.commit()
            
            if envia_email and envia_email == 'S':
                if testa_envio_email:
                    enviaremail(qtcupons, ped[4], 'brunomaya10@gmail.com', qtcupons_total, ped[0])
                else:
                    enviaremail(qtcupons, ped[4], ped[5], qtcupons_total, ped[0])
            
        cont += 1
        print(f'pedido {ped} finalizado ')

    print('todos os pedidos finalizados')
    conexao.close() 
    return 'processo finalizado, esperando contador para próximo processamento...'

# Agendamento da tarefa
#schedule.every().day.at("10:46").do(job)

# Loop principal
contador = 36000
while True:
    #schedule.run_pending()
    print(processacupom())
    data = datetime.datetime.today()
    print(data)

    # Imprima o contador decrescente
    for i in range(contador, 0, -1):
        print(f"Contador: {i}", end='\r')  # \r move o cursor de volta ao início da linha
        
        # Reduza o contador ou termine o loop, dependendo de sua lógica
        if i <= 0:
            break
        # Espere 1 segundo entre cada contagem
        time.sleep(1)