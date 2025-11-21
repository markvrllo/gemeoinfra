FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python (incluindo IA)
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    redis \
    requests \
    pandas \
    numpy \
    scikit-learn \
    matplotlib \
    seaborn \
    prometheus-client \
    gunicorn \
    tensorflow \
    joblib

# Rodamos como 'root' para ter permissão total no volume 'app_models'
WORKDIR /app

# Copiar código (como root)
COPY . /app/

# Criar diretórios de dados
RUN mkdir -p /app/{models,data,logs}

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]

