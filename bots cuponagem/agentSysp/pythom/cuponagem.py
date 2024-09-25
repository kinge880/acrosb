from conexao_postgresql import *
from conexao_oraclecaixa import *
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import datetime 
import math

def pegaUltimaVenda():
    
    conexao = createConnection()
    cursor = conexao.cursor()
    
    cursor.execute(f"""
        SELECT
            PCPEDCECF.NUMPEDECF, PCPEDCECF.NUMCAIXA, PCFILIAL.RAZAOSOCIAL, PCFILIAL.CGC, PCFILIAL.ENDERECO, PCPEDCECF."DATA"  
        FROM PCPEDCECF 
            INNER JOIN PCFILIAL ON (PCPEDCECF.CODFILIAL = PCFILIAL.CODIGO)
        ORDER BY PCPEDCECF."DATA" DESC, PCPEDCECF.NUMPEDECF DESC
    """)
    
    dados = cursor.fetchone()
    
    conexao.close()      
    return dados

def get_numcaixa():
    
    conexao = createConnection()
    cursor = conexao.cursor()
    
    cursor.execute(f"""
        SELECT
            nvl(PCPEDCECF.NUMCAIXA, 0), PCPEDCECF.CODFILIAL
        FROM PCPEDCECF 
        """)
    
    dados = cursor.fetchone()
    
    conexao.close()      
    return dados
    
def processacupom(numpedecf):
    print('iniciando...')
    conexao_postgre = conectar_banco()
    cursor_postgre = conexao_postgre.cursor()
    conexao = createConnection()
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
            acumula_intensificadores,
            autorizacao_campanha,
            regulamento,
            limite_intensificadores
        FROM 
            cpfcli_campanha
        WHERE 
            ativo = 'S' and usa_numero_da_sorte = 'N' and CURRENT_DATE between dtinit and dtfim
    ''')
    campanhas = cursor_postgre.fetchall()

    if campanhas is None and len(campanhas) > 0:
        print('Não existe campanha ativa que use cuponagem')
        return None

    result_list = []
    for campanha in campanhas:
        #parametros
        idcampanha = campanha[0]
        nomecampanha = campanha[1]
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
        autorizacao_campanha = campanha[21]
        regulamento = campanha[22]
        limite_intensificadores = campanha[23]
        
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
                marcas_list = [int(item[0]) for item in marcas]
                marcas_restringe_Where = build_clause("AND PCPRODUT.CODMARCA", marcas_list, 'IN')
            else:
                marcas_restringe_Where = ''
        #------------------------------------------------ INTENSIFICADOR POR PRODUTO --------------------------------
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
                listfornecs = [int(item[0]) for item in fornecedores]
                fornec_restringe_Where = build_clause("AND PCPRODUT.CODFORNEC", listfornecs, 'IN')
            else:
                fornec_restringe_Where = ''
                
        #---------------------------------------------------Restringe POR VALOR DO CUPOM ---------------------------------------------- 
        
        if acumulavenda and acumulavenda == 'S':
            ignora_vendas_abaixo_do_valor_cupom_having= f'''HAVING SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT) >= {valor}'''

        #---------------------------------------------------Restringe POR FILIAL ---------------------------------------------- 
        if filiais > 0:
            cursor_postgre.execute(f'''
                SELECT codfilial 
                FROM cpfcli_campanhafilial 
                WHERE idcampanha = {idcampanha}
            ''')
            filiais = cursor_postgre.fetchall()
            
            if filiais and len(filiais) > 0:
                lista_filiais = [int(item[0]) for item in filiais]
                filial_restringe_Where = build_clause("AND PCPEDCECF.CODFILIAL", lista_filiais, 'IN')
            else:
                filial_restringe_Where = ''

        #------------------------------------------------ CALCULA A BLACK LIST --------------------------------
        if cluster_cli == 'B':
            cursor_postgre.execute(f'''
                select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} AND "TIPO" = 'B'
            ''')
            black_list = cursor_postgre.fetchall()
            
            if black_list and len(black_list) > 0:
                cpflist = [int(item[0]) for item in black_list]
                blacklistWhere = build_clause("AND PCPEDCECF.CODCLI", cpflist, 'NOT')
            else:
                blacklistWhere = ''
        
        elif cluster_cli == 'W':
            cursor_postgre.execute(f'''
                select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} AND "TIPO" = 'W'
            ''')
            black_list = cursor_postgre.fetchall()
            
            if black_list and len(black_list) > 0:
                cpflist = [int(item[0]) for item in black_list]
                blacklistWhere = build_clause("AND PCPEDCECF.CODCLI", cpflist, 'IN')
            else:
                blacklistWhere = ''
        
        #------------------------------------------------ GERA A SQL PRINCIPAL --------------------------------
        print(f'''
            SELECT 
                PCPEDCECF.NUMPEDECF, 
                ROUND(SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), 2),
                TO_CHAR(PCPEDCECF."DATA", 'yyyy-mm-dd'), 
                PCPEDCECF.CODCLI,
                PCCLIENT.CLIENTE,
                PCCLIENT.EMAIL,
                PCPEDCECF.NUMCUPOM
            FROM PCPEDIECF
                INNER JOIN PCPEDCECF ON (PCPEDCECF.NUMPEDECF = PCPEDIECF.NUMPEDECF)
                INNER JOIN PCPRODUT ON (PCPEDIECF.CODPROD = PCPRODUT.CODPROD)
                INNER JOIN PCCLIENT ON (PCPEDCECF.CODCLI = PCCLIENT.CODCLI)
            WHERE 
                PCPEDCECF.NUMPEDECF = {numpedecf}
                {blacklistWhere}
                {marcas_restringe_Where}
                {listprods_restringe_where}
                {fornec_restringe_Where}
                {filial_restringe_Where}
            GROUP BY PCPEDCECF.NUMCUPOM, PCPEDCECF.NUMPEDECF, PCPEDCECF."DATA", PCPEDCECF.CODCLI, PCCLIENT.CLIENTE, PCCLIENT.EMAIL
            {ignora_vendas_abaixo_do_valor_cupom_having}
        ''')
        
        cursor.execute(f'''
            SELECT 
                PCPEDCECF.NUMPEDECF, 
                ROUND(SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), 2),
                TO_CHAR(PCPEDCECF."DATA", 'yyyy-mm-dd'), 
                PCPEDCECF.CODCLI,
                PCCLIENT.CLIENTE,
                PCCLIENT.EMAIL,
                PCPEDCECF.NUMCUPOM
            FROM PCPEDIECF
                INNER JOIN PCPEDCECF ON (PCPEDCECF.NUMPEDECF = PCPEDIECF.NUMPEDECF)
                INNER JOIN PCPRODUT ON (PCPEDIECF.CODPROD = PCPRODUT.CODPROD)
                INNER JOIN PCCLIENT ON (PCPEDCECF.CODCLI = PCCLIENT.CODCLI)
            WHERE 
                PCPEDCECF.NUMPEDECF = {numpedecf}
                {blacklistWhere}
                {marcas_restringe_Where}
                {listprods_restringe_where}
                {fornec_restringe_Where}
                {filial_restringe_Where}
            GROUP BY PCPEDCECF.NUMCUPOM, PCPEDCECF.NUMPEDECF, PCPEDCECF."DATA", PCPEDCECF.CODCLI, PCCLIENT.CLIENTE, PCCLIENT.EMAIL
            {ignora_vendas_abaixo_do_valor_cupom_having}
        ''')
        ped = cursor.fetchone()

        print('pedido pesquisados, calculando numeros da sorte')
        
        multiplicador_cupom = campanha[5]
        valor_bonus = 0
        histgeracao = ''
        saldo_atual = 0
        print(f'processando pedido {ped}')
        print(acumulavenda)
        
        #------------------------------------------------ ESCAPET CASO O PEDIDO NÃO SEJA VALIDO --------------------------------
        if ped:
        
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
                cursor_postgre.execute(f'''
                    SELECT codfornec 
                    FROM cpfcli_fornecedor 
                    where idcampanha  = {idcampanha} AND tipo IN ('I')
                ''')
                fornecedores = cursor_postgre.fetchall()
                
                if fornecedores and len(fornecedores) > 0:
                    listfornecsIntensifica = [int(item[0]) for item in fornecedores]
                
                    cursor.execute(f'''
                        SELECT SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), PCPRODUT.CODFORNEC
                        FROM PCPEDIECF
                            INNER JOIN PCPRODUT ON PCPEDIECF.CODPROD = PCPRODUT.CODPROD
                        WHERE 
                            PCPEDIECF.NUMPEDECF = {ped[0]}
                        GROUP BY PCPRODUT.CODFORNEC
                    ''')
                    valorfornecs = cursor.fetchall()

                    cont = 0
                    valor_acumulado = 0
                    if acumula_intensificador == 'A':
                        for fornecvalue in valorfornecs:
                            if fornecvalue[1] in list(listfornecsIntensifica):
                                valor_acumulado += fornecvalue[0]
                        
                        if valor_acumulado >= valor_fornecedor:
                            qtbonus = int(math.floor(valor_acumulado / valor_fornecedor))
                            valor_bonus += (multiplicador_cupom * qtbonus)
                            cont += multiplicador_cupom
                    else:
                        for fornecvalue in valorfornecs:
                            if fornecvalue[1] in list(listfornecsIntensifica):
                                if fornecvalue[0] >= valor_fornecedor:
                                    valor_bonus += multiplicador_cupom
                                    cont += multiplicador_cupom
                    
                    histgeracao += f'$$$2 - Aumentou o bônus de números da sorte baseado no fornecedor cadastrado em {cont}'
            
            #----------------------------CALCULA INTENSIFICAÇÃO POR FORNECEDOR MULTIPLO ----------------------------
            elif usa_fornec == 'M':
                print('Calculando se bonifica fornecedor Multiplo...')
                cursor.execute(f'''
                    SELECT COUNT(DISTINCT PCPRODUT.CODFORNEC)
                    FROM PCPEDIECF
                        INNER JOIN PCPRODUT ON PCPEDIECF.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDIECF.NUMPEDECF = {ped[0]}
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
                cursor_postgre.execute(f'''
                    select codmarca  
                    from cpfcli_marcas 
                    where idcampanha  = {idcampanha} AND tipo IN ('I')
                ''')
                marcas = cursor_postgre.fetchall()

                if marcas and len(marcas) > 0:
                    marcas_list_intensifica = [int(item[0]) for item in marcas]
                    
                    cursor.execute(f'''
                        SELECT SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), PCPRODUT.CODMARCA
                        FROM PCPEDIECF
                            INNER JOIN PCPRODUT ON PCPEDIECF.CODPROD = PCPRODUT.CODPROD
                        WHERE 
                            PCPEDIECF.NUMPEDECF = {ped[0]}
                        GROUP BY PCPRODUT.CODMARCA
                    ''')
                    valor_marcas = cursor.fetchall()

                    cont = 0
                    valor_acumulado = 0
                    if acumula_intensificador == 'A':
                        for valor in valor_marcas:
                            if valor[1] in marcas_list_intensifica:  # Ajuste aqui, removendo list()
                                valor_acumulado += valor[0]
                        
                        if valor_acumulado >= marca_valor:
                            qtbonus = int(math.floor(valor_acumulado / marca_valor))
                            valor_bonus += (multiplicador_cupom * qtbonus)
                            cont += multiplicador_cupom
                    else:
                        for valor in valor_marcas:
                            if valor[1] in marcas_list_intensifica:  # Certifique-se de que marcas_list é uma lista
                                if valor[0] >= marca_valor:
                                    valor_bonus += multiplicador_cupom
                                    cont += multiplicador_cupom
                    
                    histgeracao += f'$$$3 - Aumentou o bônus de números da sorte baseado na marca cadastrada em {cont}'
            
            #----------------------------CALCULA INTENSIFICAÇÃO POR MARCA MULTIPLA ----------------------------
            elif usa_marca == 'M':
                print('Calculando se bonifica MARCA Multiplo...')
                cursor.execute(f'''
                    SELECT COUNT(DISTINCT PCPRODUT.CODMARCA)
                    FROM PCPEDIECF
                        INNER JOIN PCPRODUT ON PCPEDIECF.CODPROD = PCPRODUT.CODPROD
                    WHERE 
                        PCPEDIECF.NUMPEDECF = {ped[0]}
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
                cursor_postgre.execute(f'''
                    SELECT codprod 
                    FROM cpfcli_produtos 
                    where idcampanha  = {idcampanha} AND tipo IN ('I')
                ''')
                produtos = cursor_postgre.fetchall()

                if produtos and len(produtos) > 0:
                    list_prods_intensifica = [int(item[0]) for item in produtos]
                    
                    cursor.execute(f'''
                        SELECT SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), CODPROD
                        FROM PCPEDIECF
                        WHERE PCPEDIECF.NUMPEDECF = {ped[0]}
                        GROUP BY CODPROD
                    ''')
                    prodfornecs = cursor.fetchall()
                    print(prodfornecs)
                    print(acumula_intensificador)
                    cont = 0
                    valor_acumulado = 0
                    if acumula_intensificador == 'A':
                        for prodvalue in prodfornecs:
                            if prodvalue[1] in list_prods_intensifica:
                                valor_acumulado += prodvalue[0]
                        
                        if valor_acumulado >= valor_prod:
                            qtbonus = int(math.floor(valor_acumulado / valor_prod))
                            valor_bonus += (multiplicador_cupom * qtbonus)
                            cont += multiplicador_cupom
                    else:
                        for prodvalue in prodfornecs:
                            print(prodvalue)
                            print(list_prods_intensifica)
                            if prodvalue[1] in list_prods_intensifica:
                                if prodvalue[0] >= valor_prod:
                                    valor_bonus += multiplicador_cupom
                                    cont += multiplicador_cupom

                    histgeracao += f'$$$4 - Aumentou o bônus de números da sorte baseado no produto cadastrado em {cont}'
                
            #----------------------------CALCULA INTENSIFICAÇÃO POR PRODUTO MULTIPLO ----------------------------
            elif usa_prod == 'M':
                print('Calculando se bonifica produto cadastrado...')
                cursor.execute(f'''
                    SELECT COUNT(CODPROD)
                    FROM PCPEDIECF
                    WHERE PCPEDIECF.NUMPEDECF = {ped[0]}
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
                if valor_bonus > limite_intensificadores:
                    valor_bonus = limite_intensificadores
                
                print('Calculando bonus final...')
                bonificadoWhere = 'S'
                
                if tipo_intensificador == 'M':
                    oldqtd = qtcupons
                    qtcupons = qtcupons * (multiplicador_cupom * valor_bonus)
                    histgeracao += f'$$$5 - Multiplicou os números da sorte originais {oldqtd} números, por {multiplicador_cupom} intensificadores bonus, resultando em {qtcupons} números'
                elif tipo_intensificador == 'S':
                    oldqtd = qtcupons
                    qtcupons = qtcupons + (multiplicador_cupom * valor_bonus) 
                    histgeracao += f'$$$5 - Somou os números da sorte originais {oldqtd} números, com {multiplicador_cupom} intensificadores bonus, resultando em {qtcupons} números'
                else:
                    bonificadoWhere = 'N'
            else:
                bonificadoWhere = 'N'
                histgeracao += f'$$$5 - Não foi gerado nenhum número bônus'
            
            print(qtcupons)
            cursor.execute(f'''
                SELECT CODCLI, CLIENTE, EMAIL, CGCENT, 'Cep '||CEPENT||', '||ENDERENT|| ', Número ' ||NUMEROENT , TELENT
                FROM PCCLIENT WHERE CODCLI = {ped[3]}
            ''')
            client = cursor.fetchone()
            
            if client:
                codcli = client[0] if len(client) > 0 else ''
                nomecli = client[1].replace("'", "") if len(client) > 1 and client[1] else ''
                emailcli = client[2].replace("'", "") if len(client) > 2 and client[2] else ''
                cpf_cnpj = client[3].replace("'", "") if len(client) > 3 and client[3] else ''
                telcli = client[5].replace("'", "") if len(client) > 4 and client[4] else ''
                endereco = client[4].replace("'", "") if len(client) > 5 and client[5] else ''
            
            conexao.commit()
            conexao_postgre.commit()
            
            conexao.close()
            conexao_postgre.close()
            print(histgeracao)
            result_list.append((ped[6], ped[1], codcli, nomecli, emailcli, cpf_cnpj, telcli, ped[2], bonificadoWhere, idcampanha, endereco, qtcupons, nomecampanha, autorizacao_campanha, regulamento, ped[0]))
        else:
            print(f'pedido não validado na campanha')
    print(f'busca finalizada')
    return result_list
