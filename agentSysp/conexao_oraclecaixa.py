import cx_Oracle
import os
import socket

def createConnection():
    user=os.getenv("USER_BD")
    password=os.getenv("PASSWORD")
    host=socket.gethostbyname(socket.gethostname())
    name=os.getenv("NAME")

    connection = cx_Oracle.connect(user=user, password=password, dsn=f"{host}/{name}")

    return connection



