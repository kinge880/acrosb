from instanciapastas import caminho_arquivo_cupom

def criar_cupom(nome, numcupom, razao, cnpj, endereco, fone, codcli, nomecli, telcli, cpfcli, enderecocli):
    # Usar a pasta 'Cupons' configurada anteriormente
    caminho_cupom = caminho_arquivo_cupom(numcupom)
    
    with open(caminho_cupom, 'w+') as arquivo:
        arquivo.writelines(f'RAZÃO : {razao}\n')
        arquivo.writelines(f'CNPJ : {cnpj}\n')
        arquivo.writelines(f'END : {endereco}\n')
        arquivo.writelines(f'CONTATO : {fone}\n\n')
        arquivo.writelines(f"Cupom : {numcupom}\n\n")
        arquivo.writelines("ANIVERSÁRIO ATACALE 1 ANO\n\n")
        
        if int(codcli) == 1:
            arquivo.writelines("Nome :     ____________________________________\n\n")
            arquivo.writelines("Telefone : ____________________________________\n\n")
            arquivo.writelines("CPF :      ____________________________________\n\n")
            arquivo.writelines("Endereço : ____________________________________\n\n")
        else:
            arquivo.writelines(f"Nome : {nomecli}\n\n")
            arquivo.writelines(f"Telefone : {telcli}\n\n")
            arquivo.writelines(f"CPF : {cpfcli}\n\n")
            arquivo.writelines(f"Endereço : {enderecocli}\n\n")
        
        arquivo.writelines("CERTIFICADO DE AUTORIZAÇÃO SRE/ME N. ° 06.031348/2023 PROMOÇÃO N.° 2023/07191. Mandatário: ATACALE. CNPJ: 26.554.435/0005-03")
    
    # O arquivo já foi fechado automaticamente pelo 'with'