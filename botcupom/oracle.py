


#cx_Oracle.init_oracle_client()

import cx_Oracle

#--linux--#


#cx_Oracle.init_oracle_client()

try:
    cx_Oracle.init_oracle_client()


except:


#--windows--#
    #cx_Oracle.init_oracle_client(lib_dir=r"c:\\InstantClient_21_3")

    cx_Oracle.init_oracle_client(lib_dir=r"c:\\InstantClient")

#cx_Oracle.init_oracle_client(lib_dir=r"\\192.168.0.156\\instantclient_21_3")


def conexao_oracle():
    conexao = cx_Oracle.connect("EXATAS/exat@s6410@192.168.254.26/WINT")
    #conexao = cx_Oracle.connect(user="LGBRASIL", password="LS16BR", dsn="172.16.23.20/wint")

    return conexao

