FROM python:3.9-slim

# Instalar dependências básicas
RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    iperf3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
RUN pip install --no-cache-dir \
    psutil \
    requests \
    pandas \
    numpy \
    flask \
    redis

# Rodamos como 'root' para ter permissão total no volume 'app_data'
WORKDIR /app

# Copiar código (como root)
COPY . /app/

# Criar diretórios de dados
RUN mkdir -p /app/{data,logs}

# Expor porta para API interna
EXPOSE 5001

# Comando padrão
CMD ["python", "network_simulator_docker.py"]
