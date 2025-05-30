# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.12.1-slim
LABEL maintainer="brunomaya100@gmail.com"

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Atualiza a lista de pacotes e instala gcc e outras dependências necessárias
RUN apt-get update && \
    apt-get install -y build-essential gcc libpq-dev libaio1 libnsl-dev unzip curl netcat-openbsd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./oracle/instantclient-basiclite.zip /tmp/instantclient-basiclite.zip

RUN mkdir -p /usr/lib/instantclient/network/admin && \
    cd /tmp && \
    unzip instantclient-basiclite.zip && \
    cp -r instantclient_21_18/* /usr/lib/instantclient/ && \
    rm -rf instantclient_21_18 instantclient-basiclite.zip && \
    cd /usr/lib/instantclient && \
    ln -sf libclntsh.so.21.1 libclntsh.so && \
    ln -sf libocci.so.21.1 libocci.so && \
    ls -lh /usr/lib/instantclient/

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