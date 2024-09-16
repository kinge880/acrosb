from oracle import createConnection
import re
import win32print
import ast
from criarcupom import criar_cupom
import os

def readConfig():
    file = open("C:\\SORTEIODIGITAL\\config\\config.txt", 'r', encoding='ANSI')
    txt = file.readlines()
    host = (re.sub('\n', '', str(txt[0]))).split("=")[1]
    user = (re.sub('\n', '', str(txt[1]))).split("=")[1]
    password = (re.sub('\n', '', str(txt[2]))).split("=")[1]
    database = (re.sub('\n', '', str(txt[3]))).split("=")[1]
    impressora = (re.sub('\n', '', str(txt[4]))).split("=")[1]
    img = (re.sub('\n', '', str(txt[5]))).split("=")[1]
    valor_cupom = (re.sub('\n', '', str(txt[6]))).split("=")[1]
    codfilial = (re.sub('\n', '', str(txt[7]))).split("=")[1]
    fornecs =  (re.sub('\n', '', str(txt[9]))).split("=")[1]
    listaFornecs = (re.sub('\n', '', str(txt[10]))).split("=")[1]

    lista = []

    lista.append(host)
    lista.append(user)
    lista.append(password)
    lista.append(database)
    lista.append(impressora)
    lista.append(img)
    lista.append(valor_cupom)
    lista.append(codfilial)
    lista.append(fornecs)
    lista.append(listaFornecs)
    
    
    return lista  


def pegaDadosFilial(conexao, codfilial):
    dados = ()

    try:
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT
            FANTASIA,
            substr(cgc, 1, 2) || '.' || substr(cgc, 3, 3) || '.' || substr(cgc, 6, 3) || '/' || substr(cgc, 9, 4) || '-' || substr(cgc, 13, 2) AS CNPJ,
            ENDERECO,
            '(' || substr(TELEFONE, 1,2) || ')' || ' ' || substr(TELEFONE,3,4) || '-' || substr(TELEFONE,5,4) AS FONE 
        FROM
            PCFILIAL
        WHERE 
            CODIGO = {}
        """.format(codfilial))
        
        dados = cursor.fetchone()
                
    except Exception as f:
        print("Erro ao pegar dados filial.\n{}".format(f))
    
    finally:
        return dados


def pegaUltimaVenda(conexao,numcupom,filial,numcaixa):
    dados = ()

    print(numcupom,filial,numcaixa)

    try:
        cursor = conexao.cursor()
        cursor.execute(f"""
        SELECT
            TO_CHAR("DATA", 'DD-MON-YYYY') AS "DTVENDA",
            NUMPEDECF,
            NUMCAIXA,
            PROTOCOLONFCE,
            numcupom,
            VLTOTAL,
            CODCLI,
            CODFILIAL
        FROM
            PCPEDCECF
        WHERE
            CODFILIAL = {filial}
            AND NUMCAIXA = {numcaixa}
            AND NUMCUPOM = {numcupom}
        """)
        
        dados = cursor.fetchone()
        print(dados)
                
    except Exception as f:
        print("Erro ao pegar última venda\n{}.".format(f))
    
    finally:
        return dados

def adicionarFonecs(cupom,conexao):

    listadeDados = readConfig()[9]
    
    listadeDados = ast.literal_eval(listadeDados)

    cursor = conexao.cursor()

    cursor.execute(f'''
        SELECT distinct(SELECT DISTINCT(CODFORNEC)  FROM PCPRODUT WHERE p.CODPROD = CODPROD ) fornecedor  FROM PCPEDIECF p WHERE NUMPEDECF = {cupom}
    ''')

    dados = cursor.fetchall()
   
    qtdCupons = 0

    for produt in dados:
        
        if produt[0] in listadeDados:
            
            qtdCupons +=1
            break

    print(f'''AQUI OS FORNECEDORES DOS PRODUTOS {dados}''')
    print(f'''AQUI OS FORNECEDORES DA PROMOCAO {listadeDados}''')

    return qtdCupons


def criarCupom(numcupom,filial,numcaixa,impressora):

    lista = readConfig()

    host = lista[0]
    user = lista[1]
    password = lista[2]
    database = lista[3]
    img = lista[5]
    valor_cupom = lista[6]
    codfilial = lista[7]

    win32print.SetDefaultPrinter(impressora)

    dados = pegaUltimaVenda(createConnection(),numcupom,filial,numcaixa)

    data = dados[0]
    numpedecf = dados[1]
    numcupom = dados[4]
    numcaixa = dados[2]
    protocolo = dados[3]
    vltotal = dados[5]
    codcli = dados[6]

    dadosEmpresa = pegaDadosFilial(createConnection(),codfilial)

    print(dadosEmpresa)
    razao = dadosEmpresa[0]
    cnpj = dadosEmpresa[1]
    endereco = dadosEmpresa[2]
    fone = dadosEmpresa[3]

    file = open("C:\\SORTEIODIGITAL\\config\\ultimoCupom.txt", 'r', encoding='ANSI')
    cupom = file.readlines()
    valorTxt = cupom[0]
    file.close()

    if str(readConfig()[8]) == 'S':
        cuponsFornec = adicionarFonecs(numpedecf,createConnection())
        qtdCupons = int(vltotal/int(valor_cupom))
        if int(cuponsFornec) > 0:
            qtdCupons = qtdCupons + qtdCupons
    else:
        qtdCupons = int(vltotal/int(valor_cupom))

    for i in range(qtdCupons):
        criar_cupom(i,i,razao,cnpj,endereco,fone,codcli,createConnection())
        #gera_pdf(i,img, i, razao, cnpj, endereco, fone)
        os.startfile("C:\\SORTEIODIGITAL\\cupons\\Cupom_{}.txt".format(i), "print")
       


