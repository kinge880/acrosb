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
            PCPEDCECF.NUMPEDECF, PCPEDCECF.NUMCAIXA, PCFILIAL.RAZAOSOCIAL, PCFILIAL.CGC, PCFILIAL.ENDERECO   
        FROM PCPEDCECF 
            INNER JOIN PCFILIAL ON (PCPEDCECF.CODFILIAL = PCFILIAL.CODIGO)
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
            (SELECT COUNT(codfilial) FROM cpfcli_campanhafilial WHERE idcampanha = cpfcli_campanha.idcampanha) AS total_filiais
        FROM 
            cpfcli_campanha
        WHERE 
            ativo = 'S' and usa_numero_da_sorte = 'N' and CURRENT_DATE between dtinit and dtfim
    ''')
    campanha = cursor_postgre.fetchone()

    if campanha is None:
        print('Não existe campanha ativa que use cuponagem')
        return None

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
    
    listprods_restringe_where = ''
    marcas_restringe_Where = ''
    fornec_restringe_Where = ''
    ignora_vendas_abaixo_do_valor_cupom_where = ''
    filial_restringe_Where = ''
    
    produtos_intensifica_where = ',NULL'
    produtoFornecWhere = ',NULL'
    marcas_intensifica_where = ',NULL'
    
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
            for item in marcas:
                marcas_list.extend(item[0])
            marcas_list = tuple(marcas_list)
            
            if len(marcas_list) == 1:
                marcas_restringe_Where = f'AND (SELECT COUNT(CODMARCA) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF) AND CODMARCA = {marcas_list[0]}) > 0'
            else:
                marcas_restringe_Where = f'AND (SELECT COUNT(CODMARCA) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF) AND CODMARCA IN {marcas_list}) > 0'
    
    #------------------------------------------------ INTENSIFICADOR POR PRODUTO --------------------------------
    if restringe_prod and restringe_prod == 'C':
        cursor_postgre.execute(f'''
            SELECT codprod 
            FROM cpfcli_produtos 
            where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
        ''')
        produtos = cursor_postgre.fetchall()

        if produtos and len(produtos) > 0:
            for item in produtos:
                listaprods.extend(item[0])
            listaprods = tuple(listaprods)
            
            if len(listaprods) == 1:
                listprods_restringe_where = f'AND (SELECT COUNT(CODPROD) FROM PCPEDIECF WHERE CODPROD = {listaprods[0]} AND NUMPEDECF = PCPEDCECF.NUMPEDECF) > 0'
            else:
                listprods_restringe_where = f'AND (SELECT COUNT(CODPROD) FROM PCPEDIECF WHERE CODPROD IN {listaprods} AND NUMPEDECF = PCPEDCECF.NUMPEDECF) > 0'
    
    #------------------------------------------------ RESTRIÇÃO POR FORNECEDOR --------------------------------
    if restringe_fornec and restringe_fornec == 'C':
        cursor_postgre.execute(f'''
            SELECT codfornec 
            FROM cpfcli_fornecedor 
            where idcampanha  = {idcampanha} AND tipo IN ('T', 'R')
        ''')
        fornecedores = cursor_postgre.fetchall()

        if fornecedores and len(fornecedores) > 0:
            for item in fornecedores:
                listfornecs.extend(item[0])
            listfornecs = tuple(listfornecs)

            if len(listfornecs) == 1:
                fornec_restringe_Where = f'AND (SELECT COUNT(CODFORNEC) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF) AND CODFORNEC = {listfornecs[0]}) > 0'
            else:
                fornec_restringe_Where = f'AND (SELECT COUNT(CODFORNEC) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF) AND CODFORNEC IN {listfornecs}) > 0'
    
    #---------------------------------------------------Restringe POR VALOR DO CUPOM ---------------------------------------------- 
    
    if acumulavenda and acumulavenda == 'S':
        ignora_vendas_abaixo_do_valor_cupom_where = f'''AND PCPEDCECF.VLTOTAL >= {valor}'''

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
            filial_restringe_Where = build_clause("AND PCPEDCECF.CODFILIAL", lista_filiais, 'IN')
        else:
            filial_restringe_Where = ''
        
    #---------------------------------------------------INTENSIFICADOR POR PRODUTO -----------------------------------
    if usa_prod and usa_prod == 'C':
        cursor_postgre.execute(f'''
            SELECT codprod 
            FROM cpfcli_produtos 
            where idcampanha  = {idcampanha} AND tipo IN ('I')
        ''')
        produtos = cursor_postgre.fetchall()

        if produtos and len(produtos) > 0:
            for item in produtos:
                listaprods.extend(item[0])
            listaprods = tuple(listaprods)
            
            if len(listaprods) == 1:
                produtos_intensifica_where = f',(SELECT NUMPEDECF FROM PCPEDIECF WHERE CODPROD = {listaprods[0]} AND NUMPEDECF = PCPEDCECF.NUMPEDECF AND ROWNUM = 1)'
            else:
                produtos_intensifica_where = f',(SELECT NUMPEDECF FROM PCPEDIECF WHERE CODPROD IN {listaprods} AND NUMPEDECF = PCPEDCECF.NUMPEDECF AND ROWNUM = 1)'
    elif usa_prod and usa_prod == 'M':
        produtos_intensifica_where = f',(SELECT COUNT(DISTINCT CODPROD) FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF)'

    #------------------------------------------------ INTENSIFICADOR POR FORNECEDOR --------------------------------
    if usa_fornec and usa_fornec == 'C':
        cursor_postgre.execute(f'''
            SELECT codfornec 
            FROM cpfcli_fornecedor 
            where idcampanha  = {idcampanha} AND tipo IN ('I')
        ''')
        fornecedores = cursor_postgre.fetchall()

        if fornecedores and len(fornecedores) > 0:
            for item in fornecedores:
                listfornecs.extend(item[0])
            listfornecs = tuple(listfornecs)

            if len(listfornecs) == 1:
                produtoFornecWhere = f',(SELECT NUMPEDECF FROM PCPEDIECF WHERE CODPROD IN (SELECT codprod FROM pcprodut WHERE codfornec = {listfornecs[0]}) AND NUMPEDECF = PCPEDCECF.NUMPEDECF AND ROWNUM = 1)'
            else:
                produtoFornecWhere = f',(SELECT NUMPEDECF FROM PCPEDIECF WHERE CODPROD IN (SELECT codprod FROM pcprodut WHERE codfornec IN {listfornecs}) AND NUMPEDECF = PCPEDCECF.NUMPEDECF AND ROWNUM = 1)'
    elif usa_fornec and usa_fornec == 'M':
        produtoFornecWhere = f',(SELECT COUNT(DISTINCT CODFORNEC) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF))'

    #------------------------------------------------ INTENSIFICADOR POR MARCA --------------------------------
    if usa_marca and usa_marca == 'C':
        cursor_postgre.execute(f'''
            select codmarca 
            from cpfcli_marcas 
            where idcampanha  = {idcampanha} AND tipo IN ('I')
        ''')
        marcas = cursor_postgre.fetchall()

        if marcas and len(marcas) > 0:
            for item in marcas:
                marcas_list.extend(item[0])
            marcas_list = tuple(marcas_list)

            if len(marcas_list) == 1:
                marcas_intensifica_where = f", (SELECT NUMPEDECF FROM PCPEDIECF WHERE CODPROD IN (SELECT codprod FROM pcprodut WHERE codmarca = {marcas_list[0]}) AND NUMPEDECF = PCPEDCECF.NUMPEDECF AND ROWNUM = 1)"
            else:
                marcas_intensifica_where = f", (SELECT NUMPEDECF FROM PCPEDIECF WHERE CODPROD IN (SELECT codprod FROM pcprodut WHERE codmarca = {marcas_list}) AND NUMPEDECF = PCPEDCECF.NUMPEDECF AND ROWNUM = 1)"
    elif usa_marca and usa_marca == 'M':
        marcas_intensifica_where = f',(SELECT COUNT(DISTINCT CODMARCA) FROM PCPRODUT WHERE CODPROD IN (SELECT CODPROD FROM PCPEDIECF WHERE NUMPEDECF = PCPEDCECF.NUMPEDECF))'
            
    print('iniciando pesquisa de pedidos...')

    #------------------------------------------------ CALCULA A BLACK LIST --------------------------------
    cursor_postgre.execute(f'''
        select "CODCLI" from cpfcli_blacklist where "IDCAMPANHA"  = {idcampanha} 
    ''')
    black_list = cursor_postgre.fetchall()
    
    if black_list and len(black_list) > 0:
        cpflist = [str(item[0]) for item in black_list]
        blacklistWhere = build_clause("AND PCPEDCECF.CODCLI", cpflist, 'NOT')
    else:
        blacklistWhere = ''
    
    #------------------------------------------------ GERA A SQL PRINCIPAL --------------------------------
    print(f'''
        SELECT 
            NUMPEDECF, 
            VLTOTAL,
            TO_CHAR("DATA", 'yyyy-mm-dd'), 
            CODCLI,
            (SELECT CLIENTE FROM PCCLIENT WHERE CODCLI = PCPEDCECF.CODCLI ),
            (SELECT EMAIL FROM PCCLIENT WHERE CODCLI = PCPEDCECF.CODCLI)
            {produtoFornecWhere}
            {produtos_intensifica_where}
            {marcas_intensifica_where}
        FROM PCPEDCECF
        WHERE 
            NUMPEDECF = {numpedecf}
            {ignora_vendas_abaixo_do_valor_cupom_where}
            {blacklistWhere}
            {marcas_restringe_Where}
            {listprods_restringe_where}
            {fornec_restringe_Where}
            {filial_restringe_Where}
    ''')
    
    cursor.execute(f'''
        SELECT 
            NUMPEDECF, 
            VLTOTAL,
            TO_CHAR("DATA", 'yyyy-mm-dd'), 
            CODCLI,
            (SELECT CLIENTE FROM PCCLIENT WHERE CODCLI = PCPEDCECF.CODCLI ),
            (SELECT EMAIL FROM PCCLIENT WHERE CODCLI = PCPEDCECF.CODCLI)
            {produtoFornecWhere}
            {produtos_intensifica_where}
            {marcas_intensifica_where}
        FROM PCPEDCECF
        WHERE 
            NUMPEDECF = {numpedecf}
            {ignora_vendas_abaixo_do_valor_cupom_where}
            {blacklistWhere}
            {marcas_restringe_Where}
            {listprods_restringe_where}
            {fornec_restringe_Where}
            {filial_restringe_Where}
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
    if ped is None:
        print('Pedido não validado para cuponagem')
        return None
    
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
    if usa_fornec == 'C' and ped[6] is not None:
        print('Calculando se bonifica fornecedor cadastrado...')
        cursor.execute(f'''
            SELECT SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), PCPRODUT.CODFORNEC
            FROM PCPEDIECF
                INNER JOIN PCPRODUT ON PCPEDIECF.CODPROD = PCPRODUT.CODPROD
            WHERE 
                PCPEDIECF.NUMPEDECF = {ped[0]}
            GROUP BY PCPRODUT.CODFORNEC
        ''')
        valorfornecs = cursor.featchall()

        cont = 0
        for fornecvalue in valorfornecs:
            if fornecvalue[1] in list(listfornecs):
                if fornecvalue[0] >= valor_fornecedor:
                    valor_bonus += multiplicador_cupom
                    cont += multiplicador_cupom
        
        histgeracao += f'$$$2 - Aumentou o bônus de números da sorte baseado no fornecedor cadastrado em {cont}'
    
    #----------------------------CALCULA INTENSIFICAÇÃO POR FORNECEDOR MULTIPLO ----------------------------
    elif usa_fornec == 'M' and ped[6] is not None:
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
    if usa_marca == 'C' and ped[8] is not None:
        print('Calculando se bonifica MARCA cadastrado...')
        cursor.execute(f'''
            SELECT SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), PCPRODUT.CODMARCA
            FROM PCPEDIECF
                INNER JOIN PCPRODUT ON PCPEDIECF.CODPROD = PCPRODUT.CODPROD
            WHERE 
                PCPEDIECF.NUMPEDECF = {ped[0]}
            GROUP BY PCPRODUT.CODMARCA
        ''')
        valor_marcas = cursor.featchall()

        cont = 0
        for valor in valor_marcas:
            if valor[1] in list(marcas_list):
                if valor[0] >= marca_valor:
                    valor_bonus += multiplicador_cupom
                    cont += multiplicador_cupom
        
        histgeracao += f'$$$3 - Aumentou o bônus de números da sorte baseado na marca cadastrada em {cont}'
    
    #----------------------------CALCULA INTENSIFICAÇÃO POR MARCA MULTIPLA ----------------------------
    elif usa_marca == 'M' and ped[8] is not None:
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
    if usa_prod == 'C' and ped[7] is not None:
        print('Calculando se bonifica produto cadastrado...')
        cursor.execute(f'''
            SELECT SUM(PCPEDIECF.PVENDA * PCPEDIECF.QT), CODPROD
            FROM PCPEDIECF
            WHERE PCPEDIECF.NUMPEDECF = {ped[0]}
            GROUP BY CODPROD
        ''')
        prodfornecs = cursor.featchall()
        cont = 0
        for prodvalue in prodfornecs:
            if prodvalue[1] in list(listaprods):
                if prodvalue[0] >= valor_prod:
                    valor_bonus += multiplicador_cupom
                    cont += multiplicador_cupom

        histgeracao += f'$$$4 - Aumentou o bônus de números da sorte baseado no produto cadastrado em {cont}'
        
    #----------------------------CALCULA INTENSIFICAÇÃO POR PRODUTO MULTIPLO ----------------------------
    elif usa_prod == 'M' and ped[7] is not None:
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
        SELECT CODCLI, CLIENTE, EMAIL, CGCENT, 'Cep '||CEPENT||', '||ENDERENT|| ', Número ' ||NUMEROENT 
        FROM PCCLIENT WHERE CODCLI = {ped[3]}
    ''')
    client = cursor.fetchone()
    
    if client:
        codcli = client[0] if len(client) > 0 else ''
        nomecli = client[1].replace("'", "") if len(client) > 1 and client[1] else ''
        emailcli = client[2].replace("'", "") if len(client) > 2 and client[2] else ''
        cpf_cnpj = client[3].replace("'", "") if len(client) > 3 and client[3] else ''
        telcli = client[4].replace("'", "") if len(client) > 4 and client[4] else ''
        endereco = client[5].replace("'", "") if len(client) > 5 and client[5] else ''
    
    conexao.commit()
    conexao_postgre.commit()
    
    conexao.close()
    conexao_postgre.close()
    print(f'busca finalizada')
    return (ped[0], ped[1], codcli, nomecli, emailcli, cpf_cnpj, telcli, ped[2], bonificadoWhere, idcampanha, endereco, qtcupons)
