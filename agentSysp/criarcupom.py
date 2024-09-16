
def criar_cupom(nome,numcupom,razao, cnpj, endereco, fone, codcli, conexao):

    if int(codcli) == 1:

        path = f"C:\\SORTEIODIGITAL\\cupons\\"

        arquivo = open(path+'Cupom_'+str(nome)+'.txt','w+')
        
        arquivo.writelines('RAZÃO :'+str(razao)+'\n')
        arquivo.writelines('CNPJ : '+str(cnpj)+'\n')
        arquivo.writelines('END : '+str(endereco)+'\n')
        arquivo.writelines('CONTATO : '+str(fone)+'\n\n')
        arquivo.writelines("Cupom : "+str(numcupom)+"\n\n")
        arquivo.writelines("ANIVERSÁRIO ATACALE 1 ANO\n\n")
        arquivo.writelines("Nome :     ____________________________________\n\n")
        arquivo.writelines("Telefone : ____________________________________\n\n")
        arquivo.writelines("CPF :      ____________________________________\n\n")
        arquivo.writelines("Endereço : ____________________________________\n\n")
        arquivo.writelines("CERTIFICADO DE AUTORIZAÇÃO SRE/ME N. ° 06.031348/2023 PROMOÇÃO N.° 2023/07191. Mandatário: ATACALE. CNPJ: 26.554.435/0005-03")
        arquivo.close()
    else:

        cursor = conexao.cursor()
        cursor.execute(f'''SELECT CLIENTE,COALESCE(TELENT,'VAZIO')
                        telefone ,CGCENT, ENDERENT || ' - ' || BAIRROENT AS
                        ENDERECO  FROM PCCLIENT p WHERE CODCLI = {codcli}''')

        dados = cursor.fetchall()

        path = f"C:\\SORTEIODIGITAL\\cupons\\"

        arquivo = open(path+'Cupom_'+str(nome)+'.txt','w+')
        
        arquivo.writelines('RAZÃO :'+str(razao)+'\n')
        arquivo.writelines('CNPJ : '+str(cnpj)+'\n')
        arquivo.writelines('END : '+str(endereco)+'\n')
        arquivo.writelines('CONTATO : '+str(fone)+'\n\n')
        arquivo.writelines("Cupom : "+str(numcupom)+"\n\n")
        arquivo.writelines("ANIVERSÁRIO ATACALE 1 ANO\n\n")
        arquivo.writelines("Nome : "+str(dados[0][0])+"\n\n")
        arquivo.writelines("Telefone : "+str(dados[0][1])+"\n\n")
        arquivo.writelines("CPF : "+str(dados[0][2])+"\n\n")
        arquivo.writelines("Endereço : "+str(dados[0][3])+"\n\n")
        arquivo.writelines("CERTIFICADO DE AUTORIZAÇÃO SRE/ME N. ° 06.031348/2023 PROMOÇÃO N.° 2023/07191. Mandatário: ATACALE. CNPJ: 26.554.435/0005-03")
        arquivo.close()


