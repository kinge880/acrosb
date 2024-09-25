from instanciapastas import caminho_arquivo_cupom

def criar_cupom(numcupom, razao, cnpj, endereco, fone, codcli, nomecli, cpfcli, telcli, enderecocli, nomecampanha, autorizacao_campanha, regulamento):
    # Usar a pasta 'Cupons' configurada anteriormente
    caminho_cupom = caminho_arquivo_cupom(numcupom)
    
    with open(caminho_cupom, 'w+') as arquivo:
        arquivo.writelines(f'RAZÃO : {razao}\n')
        arquivo.writelines(f'CNPJ : {cnpj}\n')
        arquivo.writelines(f'END : {endereco}\n')
        arquivo.writelines(f'CONTATO : {fone}\n\n')
        arquivo.writelines(f"Cupom : {numcupom}\n\n")
        arquivo.writelines(f"{nomecampanha}\n\n")
        
        if int(codcli) == 1 or not nomecli:
            arquivo.writelines("Nome :     ____________________________________\n\n")
        else:
            arquivo.writelines(f"Nome : {nomecli}\n\n")

        if int(codcli) == 1 or not telcli:
            arquivo.writelines("Telefone : ____________________________________\n\n")
        else:
            arquivo.writelines(f"Telefone : {telcli}\n\n")

        if int(codcli) == 1 or not cpfcli:
            arquivo.writelines("CPF :      ____________________________________\n\n")
        else:
            arquivo.writelines(f"CPF : {cpfcli}\n\n")

        if int(codcli) == 1 or not enderecocli:
            arquivo.writelines("Endereço : ____________________________________\n\n")
        else:
            arquivo.writelines(f"Endereço : {enderecocli}\n\n")
        
        arquivo.writelines(f"{autorizacao_campanha}")
    
    # O arquivo já foi fechado automaticamente pelo 'with'