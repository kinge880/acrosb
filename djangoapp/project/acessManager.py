
from .conexao_postgresql import *
from django.shortcuts import redirect
from django.contrib import messages

def test_regiao(request, id, valorperm):
    
    def _method_wrapper(view_method):

        def _arguments_wrapper(request, *args, **kwargs) :
            conexao = conectar_banco()
            cursor = conexao.cursor()
            
            cursor.execute(f'''
                SELECT idpermissao, valor, iduser
                FROM permissaoitem 
                WHERE 
                    idpermissao = {id} AND
                    valor = {valorperm} and 
                    iduser = {request.user.id}
            ''')
            permissao = cursor.fetchone()
            
            if permissao:
                return view_method(request, *args, **kwargs)
            else:
                cursor.execute(f'''
                    SELECT nomeregional
                    FROM public.regional
                    WHERE 
                        idregional = {valorperm}
                ''')
                regiao = cursor.fetchone()
                
                if regiao:
                    messages.error(f'Você não tem permissão para acessar a região {valorperm} - {regiao[0]}')
                else:
                    messages.error(f'Você tentou acessar dados de uma região com código {valorperm}, porém essa região não existe no sistema, escolha uma região válida')
                return redirect('/menu/')

        return _arguments_wrapper

    return _method_wrapper

def obterRegiao(request):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(f'''
        SELECT valor
        FROM permissaoitem 
        INNER JOIN regional ON (permissaoitem.valor = regional.idregional)
        WHERE 
            idpermissao = 1 AND
            iduser = {request.user.id}
    ''')
    
    permission = cursor.fetchall()
    result = []
    for perm  in permission:
        result.extend(perm)
    conexao.close()
    
    return result