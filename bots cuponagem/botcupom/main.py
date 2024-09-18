from conexao_postgresql import *
from oracle import *
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import datetime 
from DateFormat import dateFormat
import math

#envio de email
# Configurações do servidor SMTP
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "deeptrackemails@gmail.com"
smtp_password = "egqpqsoxbacwulkl"

""" smtp_server = "smtp.zeptomail.com"
smtp_port = 587
smtp_username = "contato@idbatacadistas.com.br"
smtp_password = "Ts0rpH5hH6Mv" """

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
        # Iniciar conexão com o servidor SMTP usando STARTTLS
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar a criptografia
        server.login(smtp_username, smtp_password)

        print('enviando')
        # Enviar e-mail
        server.sendmail(smtp_username, email, msg.as_string())
        print('encerrando')
        # Encerrar conexão
        server.quit()

def processacupom():
    print('iniciando...')
    conexao_postgre = conectar_banco()
    cursor_postgre = conexao_postgre.cursor()
    conexao = conexao_oracle()
    cursor = conexao.cursor()
    
    cursor_postgre.execute(f'''
        SELECT 
            idcampanha, 
            descricao, 
            usafornec, 
            usaprod, 
            valor, 
            multiplicador, 
            to_char(dtinit, 'yyyy-mm-dd') AS dtinit, 
            to_char(dtfim, 'yyyy-mm-dd') AS dtfim, 
            enviaemail, 
            tipointensificador, 
            fornecvalor, 
            prodvalor, 
            acumulativo, 
            usamarca, 
            marcavalor, 
            restringe_fornec, 
            restringe_marca, 
            restringe_prod,
            (SELECT COUNT(codfilial) FROM cpfcli_campanhafilial WHERE idcampanha = cpfcli_campanha.idcampanha) AS total_filiais,
            tipo_cluster_cliente,
            acumula_intensificadores
        FROM 
            cpfcli_campanha
        WHERE 
            ativo = 'S' and usa_numero_da_sorte = 'S' and CURRENT_DATE between dtinit and dtfim
    ''')
    campanhas = cursor_postgre.fetchall()

    if campanhas is None or len(campanhas) <= 0:
        return 'Não existe campanha ativa'

    for campanha in campanhas:
        #parametros
        idcampanha = campanha[0]
        usa_fornec = campanha[2]
        usa_prod = campanha[3]
        valor = campanha[4]
        dt_inicial = campanha[6]
        dt_final = campanha[7]
        envia_email = campanha[8]
        tipo_intensificador = campanha[9]
        valor_fornecedor = campanha[10]
        valor_prod = campanha[11]
        acumulavenda = campanha[12]
        testa_envio_email = True
        listaprods = []
        listfornecs = []
        marcas_list = []
        lista_filiais = []
        usa_marca = campanha[13]
        marca_valor = campanha[14]
        restringe_fornec = campanha[15]
        restringe_marca = campanha[16]
        restringe_prod = campanha[17]
        filiais = campanha[18]
        cluster_cli = campanha[19]
        acumula_intensificador = campanha[20]
        
        listprods_restringe_where = ''
        marcas_restringe_Where = ''
        fornec_restringe_Where = ''
        ignora_vendas_abaixo_do_valor_cupom_having = ''
        filial_restringe_Where = ''
        blacklistWhere = ''
        
        def divide_chunks(lst, chunk_size):
            """Divide a lista em pedaços menores de tamanho máximo chunk_size."""
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]

        def build_clause(field, values, in_or_not):
            """Constrói a cláusula NOT IN, incluindo divisão em chunks."""
            # Se houver apenas um item, retornar !=
            if len(values) == 1:
                if in_or_not == 'NOT':
                    return f"{field} != {values[0]}"
                else:
                    return f"{field} = {values[0]}"
            
            # Caso tenha mais de um item, dividir em chunks e construir várias cláusulas NOT IN
            clauses = []
            chunks = list(divide_chunks(values, 999))
            
            for chunk in chunks:
                if len(chunk) == 1:
                    if in_or_not == 'NOT':
                        clauses.append(f"{field} != {chunk[0]}")
                    else:
                        clauses.append(f"{field} = {chunk[0]}")
                else:
                    if in_or_not == 'NOT':
                        clauses.append(f"{field} NOT IN ({', '.join(map(str, chunk))})")
                    else:
                        clauses.append(f"{field} IN ({', '.join(map(str, chunk))})")
            
            # Unir todas as cláusulas com ' AND '
            return ' '.join(clauses)
        
        #------------------------------------------------RESTRIÇÃO POR MARCA --------------------------------
        if restringe_marca and restringe_marca == 'C':
            cursor_postgre.execute(f'''
                select codmarca  
                from cpfcli_marcas 
                where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
            ''')
            marcas = cursor_postgre.fetchall()

            if marcas and len(marcas) > 0:
                marcas_list = [str(item[0]) for item in marcas]
                marcas_restringe_Where = build_clause("AND PCPRODUT.CODMARCA", marcas_list, 'IN')
            else:
                marcas_restringe_Where = ''
                
        #------------------------------------------------ RESTRIÇÃO POR PRODUTO --------------------------------
        if restringe_prod and restringe_prod == 'C':
            cursor_postgre.execute(f'''
                SELECT codprod 
                FROM cpfcli_produtos 
                where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
            ''')
            produtos = cursor_postgre.fetchall()

            if produtos and len(produtos) > 0:
                listaprods = [str(item[0]) for item in produtos]
                listprods_restringe_where = build_clause("AND PCPRODUT.CODPROD", listaprods, 'IN')
            else:
                listprods_restringe_where = ''
        
        #------------------------------------------------ RESTRIÇÃO POR FORNECEDOR --------------------------------
        if restringe_fornec and restringe_fornec == 'C':
            cursor_postgre.execute(f'''
                SELECT codfornec 
                FROM cpfcli_fornecedor 
                where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
            ''')
            fornecedores = cursor_postgre.fetchall()
            
            if fornecedores and len(fornecedores) > 0:
                listfornecs = [str(item[0]) for item in fornecedores]
                fornec_restringe_Where = build_clause("AND PCPRODUT.CODFORNEC", listfornecs, 'IN')
            else:
                fornec_restringe_Where = ''
        
        #---------------------------------------------------Restringe POR VALOR DO CUPOM ---------------------------------------------- 
        
        if acumulavenda and acumulavenda == 'S':
            ignora_vendas_abaixo_do_valor_cupom_having= f'''HAVING SUM(PCPEDI.PVENDA * PCPEDI.QT) >= {valor}'''

        #---------------------------------------------------Restringe POR FILIAL ---------------------------------------------- 
        if filiais > 0:
            cursor_postgre.execute(f'''
                SELECT codfilial 
                FROM cpfcli_campanhafilial 
                WHERE idcampanha = {idcampanha}
            ''')
            filiais = cursor_postgre.fetchall()
            
            if filiais and len(filiais) > 0:
                lista_filiais = [str(item[0]) for item in filiais]
                filial_restringe_Where = build_clause("AND PCPEDC.CODFILIAL", lista_filiais, 'IN')
            else:
                filial_restringe_Where = ''

        #------------------------------------------------ CALCULA A BLACK LIST --------------------------------
        if cluster_cli == 'B':
            cursor_postgre.execute(f'''
                select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} and tipo = 'B'
            ''')
            black_list = cursor_postgre.fetchall()
            
            if black_list and len(black_list) > 0:
                cpflist = [str(item[0]) for item in black_list]
                blacklistWhere = build_clause("AND PCPEDC.CODCLI", cpflist, 'NOT')
            else:
                blacklistWhere = ''
        
        elif cluster_cli == 'W':
            cursor_postgre.execute(f'''
                select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} and tipo = 'W'
            ''')
            black_list = cursor_postgre.fetchall()
            
            if black_list and len(black_list) > 0:
                cpflist = [str(item[0]) for item in black_list]
                blacklistWhere = build_clause("AND PCPEDC.CODCLI", cpflist, 'IN')
            else:
                blacklistWhere = ''

        #------------------------------------------------ CALCULA OS PEDIDOS JÁ PROCESSADOS --------------------------------
        cursor_postgre.execute(f'''
            SELECT DISTINCT NUMPED
            FROM cpfcli_campanhaprocessados
            WHERE IDCAMPANHA = {idcampanha}
        ''')
        list_numpeds = cursor_postgre.fetchall()
        
        if list_numpeds and len(list_numpeds) > 0:
            numped_list_postgre = [str(item[0]) for item in list_numpeds]
            not_in_clauses = build_clause("AND PCPEDC.NUMPED", numped_list_postgre, 'NOT')
        else:
            not_in_clauses = ''
        
        #------------------------------------------------ GERA A SQL PRINCIPAL --------------------------------
        print(f'''
            SELECT 
                PCPEDC.NUMPED, 
                ROUND(SUM(PCPEDI.PVENDA * PCPEDI.QT), 2),
                TO_CHAR(PCPEDC."DATA", 'yyyy-mm-dd'), 
                PCPEDC.CODCLI,
                PCCLIENT.CLIENTE,
                PCCLIENT.EMAIL
            FROM PCPEDI 
                INNER JOIN PCPEDC ON (PCPEDC.NUMPED = PCPEDI.NUMPED)
                INNER JOIN PCPRODUT ON (PCPEDI.CODPROD = PCPRODUT.CODPROD)
                INNER JOIN PCCLIENT ON (PCPEDC.CODCLI = PCCLIENT.CODCLI)
            WHERE 
                PCPEDC."DATA" BETWEEN to_date('2024-09-17', 'yyyy-mm-dd') AND to_date('2024-09-18', 'yyyy-mm-dd') AND
                PCPEDC.POSICAO = 'F' AND 
                PCPEDC.ORIGEMPED IN ('F', 'T', 'R', 'B', 'A') AND
                PCPEDC.CONDVENDA != 10
                NOT EXISTS (
                    SELECT NUMPED 
                    FROM MSCUPONAGEMCAMPANHAPROCESSADOS 
                    WHERE NUMPED = PCPEDC.NUMPED 
                    AND IDCAMPANHA = {idcampanha}
                )
                {blacklistWhere}
                {marcas_restringe_Where}
                {listprods_restringe_where}
                {fornec_restringe_Where}
                {filial_restringe_Where}
            GROUP BY PCPEDC.NUMPED, PCPEDC."DATA", PCPEDC.CODCLI, PCCLIENT.CLIENTE, PCCLIENT.EMAIL
            {ignora_vendas_abaixo_do_valor_cupom_having}
        ''')
        
        cursor.execute(f'''
            SELECT 
                PCPEDC.NUMPED, 
                ROUND(SUM(PCPEDI.PVENDA * PCPEDI.QT), 2),
                TO_CHAR(PCPEDC."DATA", 'yyyy-mm-dd'), 
                PCPEDC.CODCLI,
                PCCLIENT.CLIENTE,
                PCCLIENT.EMAIL
            FROM PCPEDI 
                INNER JOIN PCPEDC ON (PCPEDC.NUMPED = PCPEDI.NUMPED)
                INNER JOIN PCPRODUT ON (PCPEDI.CODPROD = PCPRODUT.CODPROD)
                INNER JOIN PCCLIENT ON (PCPEDC.CODCLI = PCCLIENT.CODCLI)
            WHERE 
                PCPEDC."DATA" BETWEEN to_date('2024-09-17', 'yyyy-mm-dd') AND to_date('2024-09-18', 'yyyy-mm-dd') AND
                PCPEDC.POSICAO = 'F' AND 
                PCPEDC.ORIGEMPED IN ('F', 'T', 'R', 'B', 'A') AND
                PCPEDC.CONDVENDA != 10 AND 
                NOT EXISTS (
                    SELECT NUMPED 
                    FROM MSCUPONAGEMCAMPANHAPROCESSADOS 
                    WHERE NUMPED = PCPEDC.NUMPED 
                    AND IDCAMPANHA = {idcampanha}
                )
                {blacklistWhere}
                {marcas_restringe_Where}
                {listprods_restringe_where}
                {fornec_restringe_Where}
                {filial_restringe_Where}
            GROUP BY PCPEDC.NUMPED, PCPEDC."DATA", PCPEDC.CODCLI, PCCLIENT.CLIENTE, PCCLIENT.EMAIL
            {ignora_vendas_abaixo_do_valor_cupom_having}
        ''')
        pedidos = cursor.fetchall()

        print('pedidos pesquisados, calculando numeros da sorte')
        contador = 1
        
        for ped in pedidos:
            multiplicador_cupom = campanha[5]
            valor_bonus = 0
            histgeracao = ''
            saldo_atual = 0
            print(f'processando pedido {ped} posição {contador} de {len(pedidos)}')
            print(acumulavenda)
            
            #------------------------------------------------ COMEÇA A CALCULAR O SALDO --------------------------------
            if acumulavenda in ('S', 'T'):
                print('Calculando se existe saldo...')
                # Busca saldo do cliente na tabela cpfcli_cuponagemsaldo
                cursor_postgre.execute(f'''
                    select saldo 
                    FROM cpfcli_cuponagemsaldo 
                    WHERE 
                        codcli = {ped[3]} AND 
                        idcampanha = {idcampanha}
                ''')
                saldo_cli = cursor_postgre.fetchone()

                if saldo_cli:
                    saldo_atual = saldo_cli[0]
                
                # Calcula cupons
                qtcupons = int(math.floor((ped[1] + saldo_atual) / valor))
                histgeracao += f'0 - Calculou uma quantidade de {qtcupons} números'
                
                # Calcula a sobra
                sobra = (ped[1] + saldo_atual) % valor
                
                if sobra and saldo_cli:
                    # Atualiza o saldo na tabela cpfcli_cuponagemsaldo
                    cursor_postgre.execute(f'''
                        UPDATE cpfcli_cuponagemsaldo 
                        SET 
                            saldo = {sobra}, 
                            dtmov = NOW() 
                        WHERE 
                            codcli = {ped[3]} AND 
                            idcampanha = {idcampanha}
                    ''')
                    histgeracao += f'$$$1 - Calculou uma sobra de R$ {sobra}'
                
                elif sobra:
                    # Insere um novo saldo na tabela cpfcli_cuponagemsaldo
                    if ped[4]:
                        nomecli = ped[4].replace("'", "")
                    else:
                        nomecli = ped[4]
                    if ped[4]:
                        emailcli = ped[4].replace("'", "")
                    else:
                        emailcli = ped[4]
                        
                    cursor_postgre.execute(f'''
                        insert into cpfcli_cuponagemsaldo
                        (codcli, idcampanha, saldo, dtmov, nomecli, emailcli)
                        VALUES ({ped[3]}, {idcampanha}, {sobra}, NOW(), '{nomecli}', '{emailcli}')
                    ''')
                    histgeracao += f'$$$1 - Calculou uma sobra de R$ {sobra}'
                
                print('Saldo calculado...')
            
            else:
                qtcupons = int(math.floor(ped[1] / valor))
                histgeracao += f'0 - Calculou uma quantidade de {qtcupons} números'
                histgeracao += f'$$$1 - Nenhuma sobra calculada'
                print('1 - Sobra não calculada...')
            
            #----------------------------CALCULA INTENSIFICAÇÃO POR FORNECEDOR CADASTRADO ----------------------------
            if usa_fornec == 'C':
                print('Calculando se bonifica fornecedor cadastrado...')
                cursor.execute(f'''
                    SELECT SUM(PCPEDI.PVENDA * PCPEDI.QT), PCPRODUT.CODFORNEC
                    FROM PCPEDI
                        INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDI.NUMPED = {ped[0]}
                    GROUP BY PCPRODUT.CODFORNEC
                ''')
                valorfornecs = cursor.fetchall()

                cont = 0
                valor_acumulado = 0
                if acumula_intensificador == 'A':
                    for fornecvalue in valorfornecs:
                        if fornecvalue[1] in list(listfornecs):
                            valor_acumulado += fornecvalue[0]
                    
                    if valor_acumulado >= valor_fornecedor:
                        qtbonus = int(math.floor(valor_acumulado / valor_fornecedor))
                        valor_bonus += (multiplicador_cupom * qtbonus)
                        cont += multiplicador_cupom
                else:
                    for fornecvalue in valorfornecs:
                        if fornecvalue[1] in list(listfornecs):
                            if fornecvalue[0] >= valor_fornecedor:
                                valor_bonus += multiplicador_cupom
                                cont += multiplicador_cupom
                
                
                histgeracao += f'$$$2 - Aumentou o bônus de números da sorte baseado no fornecedor cadastrado em {cont}'
            
            #----------------------------CALCULA INTENSIFICAÇÃO POR FORNECEDOR MULTIPLO ----------------------------
            elif usa_fornec == 'M':
                print('Calculando se bonifica fornecedor Multiplo...')
                cursor.execute(f'''
                    SELECT COUNT(DISTINCT PCPRODUT.CODFORNEC)
                    FROM PCPEDI
                        INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDI.NUMPED = {ped[0]}
                ''')
                qtfornecs = cursor.fetchone()

                cont = 0
                
                if qtfornecs[0] >= valor_fornecedor:
                    valor_bonus += multiplicador_cupom
                    cont += multiplicador_cupom
                
                histgeracao += f'$$$2 - Aumentou o bônus de números da sorte baseado no fornecedor multiplo em {cont}'
            
            else:
                histgeracao += f'$$$2 - Não houve bônus de números da sorte baseado no fornecedor'
                
                #----------------------------CALCULA INTENSIFICAÇÃO POR MARCA CADASTRADA ----------------------------
            if usa_marca == 'C':
                print('Calculando se bonifica MARCA cadastrado...')
                cursor.execute(f'''
                    SELECT SUM(PCPEDI.PVENDA * PCPEDI.QT), PCPRODUT.CODMARCA
                    FROM PCPEDI
                        INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDI.NUMPED = {ped[0]}
                    GROUP BY PCPRODUT.CODMARCA
                ''')
                valor_marcas = cursor.fetchall()

                cont = 0
                valor_acumulado = 0
                if acumula_intensificador == 'A':
                    for valor in valor_marcas:
                        if valor[1] in marcas_list:  # Ajuste aqui, removendo list()
                            valor_acumulado += valor[0]
                    
                    if valor_acumulado >= marca_valor:
                        qtbonus = int(math.floor(valor_acumulado / marca_valor))
                        valor_bonus += (multiplicador_cupom * qtbonus)
                        cont += multiplicador_cupom
                else:
                    for valor in valor_marcas:
                        if valor[1] in marcas_list:  # Certifique-se de que marcas_list é uma lista
                            if valor[0] >= marca_valor:
                                valor_bonus += multiplicador_cupom
                                cont += multiplicador_cupom
                
                histgeracao += f'$$$3 - Aumentou o bônus de números da sorte baseado na marca cadastrada em {cont}'
            
            #----------------------------CALCULA INTENSIFICAÇÃO POR MARCA MULTIPLA ----------------------------
            elif usa_marca == 'M':
                print('Calculando se bonifica MARCA Multiplo...')
                cursor.execute(f'''
                    SELECT COUNT(DISTINCT PCPRODUT.CODMARCA)
                    FROM PCPEDI
                        INNER JOIN PCPRODUT ON PCPEDI.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDI.NUMPED = {ped[0]}
                ''')
                qtmarcas = cursor.fetchone()

                cont = 0
                
                if qtmarcas[0] >= marca_valor:
                    valor_bonus += multiplicador_cupom
                    cont += multiplicador_cupom
                
                histgeracao += f'$$$3 - Aumentou o bônus de números da sorte baseado na marca multipla em {cont}'
            
            else:
                histgeracao += f'$$$3 - Não houve bônus de números da sorte baseado na marca'
                
            #----------------------------CALCULA INTENSIFICAÇÃO POR PRODUTO CADASTRADO ----------------------------
            if usa_prod == 'C':
                print('Calculando se bonifica produto cadastrado...')
                cursor.execute(f'''123377
                    SELECT SUM(PCPEDI.PVENDA * PCPEDI.QT), CODPROD
                    FROM PCPEDI
                    WHERE PCPEDI.NUMPED = {ped[0]}
                    GROUP BY CODPROD
                ''')
                prodfornecs = cursor.fetchall()
                
                cont = 0
                valor_acumulado = 0
                if acumula_intensificador == 'A':
                    for prodvalue in prodfornecs:
                        if prodvalue[1] in listaprods:
                            valor_acumulado += prodvalue[0]
                    
                    if valor_acumulado >= valor_prod:
                        qtbonus = int(math.floor(valor_acumulado / valor_prod))
                        valor_bonus += (multiplicador_cupom * qtbonus)
                        cont += multiplicador_cupom
                else:
                    for prodvalue in prodfornecs:
                        if prodvalue[1] in listaprods:
                            if prodvalue[0] >= valor_prod:
                                valor_bonus += multiplicador_cupom
                                cont += multiplicador_cupom

                histgeracao += f'$$$4 - Aumentou o bônus de números da sorte baseado no produto cadastrado em {cont}'
                
            #----------------------------CALCULA INTENSIFICAÇÃO POR PRODUTO MULTIPLO ----------------------------
            elif usa_prod == 'M':
                print('Calculando se bonifica produto cadastrado...')
                cursor.execute(f'''
                    SELECT COUNT(CODPROD)
                    FROM PCPEDI
                    WHERE PCPEDI.NUMPED = {ped[0]}
                ''')
                qtprods = cursor.fetchone()
                cont = 0
                
                if qtprods[0] >= valor_prod:
                    valor_bonus += multiplicador_cupom
                    cont += multiplicador_cupom

                histgeracao += f'$$$4 - Aumentou o bônus de números da sorte baseado no produto cadastrado em {cont}'
            
            else:
                histgeracao += f'$$$4 - Não houve bônus de números da sorte baseado no produto'
                
            #--------------------------------------APLICANDO BONUS NO CUPOM ORIGINAL GERAL ------------------------------------------
            if valor_bonus > 0:
                print('Calculando bonus final...')
                bonificadoWhere = 'S'
                
                if tipo_intensificador == 'M':
                    oldqtd = qtcupons
                    qtcupons = qtcupons * multiplicador_cupom
                    histgeracao += f'$$$5 - Multiplicou os números da sorte originais {oldqtd} números, por {multiplicador_cupom} intensificadores bonus, resultando em {qtcupons} números'
                elif tipo_intensificador == 'S':
                    oldqtd = qtcupons
                    qtcupons = qtcupons + multiplicador_cupom
                    histgeracao += f'$$$5 - Somou os números da sorte originais {oldqtd} números, com {multiplicador_cupom} intensificadores bonus, resultando em {qtcupons} números'
                else:
                    bonificadoWhere = 'N'
            else:
                bonificadoWhere = 'N'
                histgeracao += f'$$$5 - Não foi gerado nenhum número bônus'
            
            print(qtcupons)
            cursor.execute(f'''
                SELECT CODCLI, CLIENTE, EMAIL, CGCENT, TELCOB FROM PCCLIENT WHERE CODCLI = {ped[3]}
            ''')
            client = cursor.fetchone()
            
            if client:
                codcli = client[0] if len(client) > 0 else ''
                nomecli = client[1].replace("'", "") if len(client) > 1 and client[1] else ''
                emailcli = client[2].replace("'", "") if len(client) > 2 and client[2] else ''
                cpf_cnpj = client[3].replace("'", "") if len(client) > 3 and client[3] else ''
                telcli = client[4].replace("'", "") if len(client) > 4 and client[4] else ''
                    
            if qtcupons >= 1:
                for i in range(qtcupons):
                    print(f'Gerando número da sorte pedido {ped[0]} volume {i + 1} de {qtcupons}')
                    
                    cursor_postgre.execute(f'''
                        INSERT INTO cpfcli_cuponagem
                        (id, dtmov, numped, valor, numsorte, codcli, nomecli, emailcli, telcli, cpf_cnpj, dataped, bonificado, ativo, idcampanha, numcaixa, numpedecf, tipo)
                        VALUES (
                            DEFAULT, 
                            NOW(), 
                            {ped[0]},  -- Número do pedido
                            {ped[1]},  -- Valor total
                            (SELECT COALESCE(MAX(numsorte), 0) + 1 FROM cpfcli_cuponagem WHERE idcampanha = {idcampanha} ),
                            {codcli},  -- Código do cliente
                            '{nomecli}', 
                            '{emailcli}', 
                            '{telcli}', 
                            '{cpf_cnpj}', 
                            '{ped[2]}',  -- Data do pedido
                            '{bonificadoWhere}',         -- Bonificado (ajustar conforme necessário)
                            'S',        -- Ativo
                            {idcampanha}, -- ID da campanha
                            NULL,
                            NULL,
                            'NS'
                        )
                    ''')

                # Inserção em cpfcli_campanhaprocessados
                cursor_postgre.execute(f'''
                    INSERT INTO cpfcli_campanhaprocessados
                    (id, idcampanha, codcli, dtmov, historico, numped, geroucupom, geroubonus)
                    VALUES (
                        DEFAULT, 
                        {idcampanha},  -- ID da campanha
                        {codcli},      -- Código do cliente
                        NOW(),         -- Data de movimento
                        '{histgeracao}',  -- Histórico
                        {ped[0]},       -- Número do pedido
                        'S',
                        '{bonificadoWhere}'
                    )
                ''')
                
                # Inserção em cpfcli_campanhaprocessados
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMCAMPANHAPROCESSADOS
                    (NUMPED, IDCAMPANHA, DTMOV, HISTORICO, CODCLI, GEROUCUPOM, GEROUBONUS)
                    VALUES (
                        {ped[0]},           -- Número do pedido
                        {idcampanha},       -- ID da campanha
                        SYSDATE,              -- Data de movimento
                        '{histgeracao}',    -- Histórico de geração
                        {codcli},           -- Código do cliente
                        'S',                -- Gerou cupom (Sim)
                        '{bonificadoWhere}' -- Gerou bônus (Depende da condição)
                    )
                ''')
                
                cursor_postgre.execute(f'''
                    SELECT count(DISTINCT numsorte) from cpfcli_cuponagem where codcli = {ped[3]}
                ''')
                qtcupons_total = cursor_postgre.fetchone()
                
                if envia_email and envia_email == 'S':
                    if testa_envio_email:
                        enviaremail(qtcupons, ped[4], 'brunomaya10@gmail.com', qtcupons_total, ped[0])
                    else:
                        enviaremail(qtcupons, ped[4], ped[5], qtcupons_total, ped[0])
            else:
                cursor_postgre.execute(f'''
                    INSERT INTO cpfcli_campanhaprocessados
                    (id, idcampanha, codcli, dtmov, historico, numped, geroucupom, geroubonus)
                    VALUES (
                        DEFAULT, 
                        {idcampanha},  -- ID da campanha
                        {codcli},      -- Código do cliente
                        NOW(),         -- Data de movimento
                        '{histgeracao}',  -- Histórico
                        {ped[0]},       -- Número do pedido
                        'N',
                        '{bonificadoWhere}'
                    )
                ''') 
                
                # Inserção em cpfcli_campanhaprocessados
                cursor.execute(f'''
                    INSERT INTO MSCUPONAGEMCAMPANHAPROCESSADOS
                    (NUMPED, IDCAMPANHA, DTMOV, HISTORICO, CODCLI, GEROUCUPOM, GEROUBONUS)
                    VALUES (
                        {ped[0]},           -- Número do pedido
                        {idcampanha},       -- ID da campanha
                        SYSDATE,              -- Data de movimento
                        '{histgeracao}',    -- Histórico de geração
                        {codcli},           -- Código do cliente
                        'N',                -- Gerou cupom (Não)
                        '{bonificadoWhere}' -- Gerou bônus (Condição)
                    )
                ''')
                
            contador += 1
            conexao.commit()
            conexao_postgre.commit()
            print(f'pedido finalizado ')

        print('todos os pedidos finalizados')
        conexao.close() 
        conexao_postgre.close()
    return 'processo finalizado, esperando contador para próximo processamento...'

# Agendamento da tarefa
#schedule.every().day.at("10:46").do(job)

# Loop principal
contador = 60
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