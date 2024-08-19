FROM python:3.12.1-alpine3.18
LABEL maintainer="brunomaya100@gmail.com"

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Atualiza a lista de pacotes e instala gcc e outras dependências necessárias
RUN apk update && \
    apk add --no-cache build-base gcc musl-dev postgresql-dev libaio libnsl libc6-compat curl

# Instala o Oracle Instant Client
RUN cd /tmp && \
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

# Copia o arquivo de configuração do TNS
COPY ./tnsnames.ora /usr/lib/instantclient/network/admin/tnsnames.ora

ENV LD_LIBRARY_PATH /usr/lib/instantclient
ENV TNS_ADMIN /usr/lib/instantclient/network/admin

# Copia as pastas "djangoapp" e "scripts" para dentro do container
COPY ./djangoapp /djangoapp
COPY ./scripts /scripts

# Define o diretório de trabalho
WORKDIR /djangoapp

# Instala o Gunicorn e outras dependências Python
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /djangoapp/requirements.txt && \
    adduser --disabled-password --no-create-home duser && \
    mkdir -p /data/web/static && \
    mkdir -p /data/web/media && \
    chown -R duser:duser /venv /data/web/static /data/web/media /scripts && \
    chmod -R 755 /data/web/static /data/web/media && \
    chmod -R +x /scripts

# Adiciona a pasta "scripts" e "/venv/bin" ao PATH do container
ENV PATH="/scripts:/venv/bin:$PATH"

# Muda o usuário para duser
USER duser

# Expõe a porta que o Gunicorn usará
EXPOSE 8000

# Executa o arquivo scripts/commands.sh
CMD ["commands.sh", "gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
