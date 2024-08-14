FROM python:3.12.1-alpine3.18
LABEL maintainer="brunomaya100@gmail.com"

# Essa variável de ambiente é usada para controlar se o Python deve 
# gravar arquivos de bytecode (.pyc) no disco. 1 = Não, 0 = Sim
ENV PYTHONDONTWRITEBYTECODE 1

# Define que a saída do Python será exibida imediatamente no console ou em 
# outros dispositivos de saída, sem ser armazenada em buffer.
# Em resumo, você verá os outputs do Python em tempo real.
ENV PYTHONUNBUFFERED 1

# Atualiza a lista de pacotes e instala gcc e outras dependências necessárias
RUN apk update && \
    apk add --no-cache build-base && \
    apk add --no-cache postgresql-dev  # Adicione outras dependências se necessário

RUN apk --no-cache add libaio libnsl libc6-compat curl && \
cd /tmp && \
curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/2114000/instantclient-basiclite-linux.x64-21.14.0.0.0dbru.zip -SL && \
unzip instantclient-basiclite.zip && \
mv instantclient*/ /usr/lib/instantclient && \
rm instantclient-basiclite.zip && \
ln -s /usr/lib/instantclient/libclntsh.so.21.1 /usr/lib/libclntsh.so && \
ln -s /usr/lib/instantclient/libocci.so.21.1 /usr/lib/libocci.so && \
ln -s /usr/lib/instantclient/libociicus.so /usr/lib/libociicus.so && \
ln -s /usr/lib/instantclient/libnnz21.so /usr/lib/libnnz21.so && \
ln -s /usr/lib/libnsl.so.2 /usr/lib/libnsl.so.1 && \
ln -s /lib/libc.so.6 /usr/lib/libresolv.so.2 && \
ln -s /lib64/ld-linux-x86-64.so.2 /usr/lib/ld-linux-x86-64.so.2

COPY ./tnsnames.ora /usr/lib/instantclient/network/admin/tnsnames.ora

ENV LD_LIBRARY_PATH /usr/lib/instantclient
ENV TNS_ADMIN /usr/lib/instantclient/network/admin

# Copia a pasta "djangoapp" e "scripts" para dentro do container.
COPY ./djangoapp /djangoapp
COPY ./scripts /scripts

# Entra na pasta djangoapp no container
WORKDIR /djangoapp

# A porta 8000 estará disponível para conexões externas ao container
# É a porta que vamos usar para o Django.
EXPOSE 8000

# RUN executa comandos em um shell dentro do container para construir a imagem. 
# O resultado da execução do comando é armazenado no sistema de arquivos da 
# imagem como uma nova camada.
# Agrupar os comandos em um único RUN pode reduzir a quantidade de camadas da 
# imagem e torná-la mais eficiente.
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /djangoapp/requirements.txt && \
    adduser --disabled-password --no-create-home duser && \
    mkdir -p /data/web/static && \
    mkdir -p /data/web/media && \
    chown -R duser:duser /venv && \
    chown -R duser:duser /data/web/static && \
    chown -R duser:duser /data/web/media && \
    chmod -R 755 /data/web/static && \
    chmod -R 755 /data/web/media && \
    chmod -R +x /scripts
 
# Adiciona a pasta scripts e venv/bin 
# no $PATH do container.
ENV PATH="/scripts:/venv/bin:$PATH"

# Muda o usuário para duser
USER duser

# Executa o arquivo scripts/commands.sh
CMD ["commands.sh"]