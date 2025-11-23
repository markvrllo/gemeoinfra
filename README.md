# Gêmeo Digital para Monitoramento de Desempenho de Rede

## 📋 Resumo Executivo

Este projeto implementa um **Gêmeo Digital (Digital Twin)** completo para simulação, monitoramento, detecção de anomalias e previsão de métricas de desempenho de rede. A solução é **100% containerizada** utilizando Docker Compose e integra:

- **Simulador de rede** com geração sintética de métricas
- **API REST** com engine de análise e previsão
- **Machine Learning**: Detecção de anomalias (Isolation Forest) e previsão (LSTM)
- **Stack de monitoramento**: Prometheus + Grafana para observabilidade
- **Cache distribuído**: Redis para buffer leve
- **Proxy reverso**: Nginx como gateway único

### Informações de Acesso

```bash
# SSH - Máquina Virtual
ssh ginfragrad05@cloudgrad.icmc.usp.br -p <porta>
senha: Lq4xzVR4

# Web - Dashboard
http://cloudgrad.icmc.usp.br:5191/
http://cloudgrad.icmc.usp.br:5191/grafana/
http://cloudgrad.icmc.usp.br:5191/prometheus/
```

---

## 🏗️ Arquitetura da Solução

### Visão Geral em Camadas

```
┌─────────────────────────────────────────────────────────┐
│           Acesso Externo (Usuário/Admin)                │
│        cloudgrad.icmc.usp.br:5191 (Nginx)              │
└─────────────────┬───────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌─────────────┐  ┌──────────────┐
    │   Grafana   │  │ Prometheus   │
    │  :3000      │  │   :9090      │
    └─────────────┘  └──────────────┘
         │                 │
         └────────┬────────┘
                  ▼
    ┌──────────────────────────────┐
    │   Digital Twin API           │
    │   (DigitalTwinEngine)         │
    │   • Anomaly Detection        │
    │   • LSTM Predictions         │
    │   :5000                      │
    └──────────────────────────────┘
         │         │         │
         ▼         ▼         ▼
    ┌────────┐ ┌─────┐ ┌──────────┐
    │Simulator│ │Redis │ │ Models  │
    │:5001   │ │:6379│ │(ML)     │
    └────────┘ └─────┘ └──────────┘
         │         │
         └────┬────┘
              ▼
    ┌──────────────────┐
    │   CSV Storage    │
    │  /app/data/*csv  │
    └──────────────────┘
```

### Componentes Principais

#### 1. **Simulador de Rede** (`network_simulator_docker.py`)
- Aplicação Flask que gera métricas sintéticas
- **6 Hosts + 3 Switches** simulados
- Geração de 10 métricas por elemento, a cada **10 segundos**
- Outputs: CSV (persistência) + JSON (Redis) + Prometheus format

**Endpoints:**
```bash
GET  /health                 # Status de saúde
POST /start_simulation       # Inicia coleta
POST /stop_simulation        # Para e salva
GET  /get_data              # Últimas métricas (JSON)
GET  /metrics               # Prometheus format
```

**Métricas Geradas (10 por host/switch):**
1. `cpu_usage` - Percentual CPU (0-100%)
2. `memory_usage` - Percentual RAM (0-100%)
3. `latency_ms` - Latência em ms
4. `jitter_ms` - Variação de latência
5. `packet_loss_percent` - Perda de pacotes (%)
6. `network_rx_bytes` - Bytes recebidos/s
7. `network_tx_bytes` - Bytes transmitidos/s
8. `tcp_connections` - Conexões TCP ativas
9. `network_errors` - Erros de rede/s
10. `switch_buffer_utilization` - Buffer switches (%)

#### 2. **Digital Twin API** (`app.py`)
- Motor central de análise e previsão
- **Classe DigitalTwinEngine**: Orquestra detecção + previsão
- Detecção online de anomalias (Isolation Forest)
- Previsões com modelo LSTM pré-treinado
- Agregação de métricas em formato Prometheus

**Endpoints Principais:**
```bash
GET  /                       # UI de controle
GET  /health                # Status
POST /simulation/start      # Controla simulador
POST /simulation/stop       # Controla simulador
POST /analysis/anomalies    # Detecção de anomalias
POST /predict              # Previsões LSTM
GET  /metrics              # Métricas em Prometheus
```

#### 3. **Redis Cache** (Port 6379)
- Armazenamento temporário de métricas
- Lista `network_metrics` com últimas 500 amostras
- Buffer leve entre simulador e API
- TTL configurável

#### 4. **Prometheus** (Port 9090)
- Banco de dados de séries temporais (TSDB)
- Scrape de targets a cada **15 segundos**
  - Target 1: `api:5000/metrics` (previsões + anomalias)
  - Target 2: `simulator:5001/metrics` (métricas reais)
- Retenção padrão: 15 dias
- Queries PromQL disponíveis

#### 5. **Grafana** (Port 3000)
- Visualização em tempo real
- Dashboards customizáveis com:
  - Gráficos de série temporal
  - Heatmaps de anomalias
  - Previsões sobrepostas
  - Alertas por threshold
- DataSource: Prometheus

#### 6. **Nginx** (Port 80 → 5191 externo)
- Proxy reverso e gateway único
- Upstreams:
  - `/` → `api:5000`
  - `/grafana/` → `grafana:3000`
  - `/prometheus/` → `prometheus:9090`
- Acesso externo: `http://cloudgrad.icmc.usp.br:5191`

---

## 🤖 Modelos de Machine Learning

### Detecção de Anomalias

**Algoritmo:** Isolation Forest + StandardScaler

- **Contaminação:** 0.1 (anomalias esperadas em 0.1% dos dados)
- **Features:** 10 métricas de rede normalizadas
- **Treinamento:** Online
  - 1ª batch: treina o modelo
  - Batches posteriores: predizem anomalias
- **Output:** Score de anomalia por amostra (quanto maior, mais anômalo)

```python
# Execução
POST /analysis/anomalies
{
  "response": {
    "anomalies_detected": 3,
    "anomaly_scores": [0.12, 0.89, 0.11, 0.05, ...]
  }
}
```

### Previsão com LSTM

**Arquitetura do Modelo:**
```
Input (batch, 10, 10)  # 10 time-steps, 10 features
    ↓
LSTM Layer 1 (64 units, return_sequences=True)
    ↓
Dropout (0.2)
    ↓
LSTM Layer 2 (64 units)
    ↓
Dropout (0.2)
    ↓
Dense (10 units) → Output (batch, 10) # 10 features
```

**Treinamento:**
- **Epochs:** 50 com Early Stopping
- **Batch size:** 32
- **Validation split:** 20%
- **Pré-processamento:** MinMaxScaler (normaliza em [-1, 1])
- **Loss:** MSE (Mean Squared Error)

**Execução de Previsão:**
```bash
POST /predict
Response:
{
  "predictions": {
    "cpu_usage": 47.3,
    "memory_usage": 65.8,
    "latency_ms": 13.2,
    ...
  },
  "timestamp": "2025-01-20T10:00:30Z"
}
```

**Modelo e Scaler:**
- `network_model_full.h5` - Modelo Keras/LSTM
- `scaler_full.joblib` - Normalizador (joblib)
- Localização: `/app/models/`

---

## 📊 Formatos de Dados

### CSV (Persistência)
```csv
timestamp,host_id,type,cpu_usage,memory_usage,latency_ms,jitter_ms,packet_loss_percent,network_rx_bytes,network_tx_bytes,tcp_connections,network_errors,switch_buffer_utilization
2025-01-20 10:00:00,host-1,host,45.2,62.1,12.5,0.3,0.1,1024000,512000,42,0,28.5
2025-01-20 10:00:00,switch-1,switch,0.0,0.0,8.2,0.1,0.05,5120000,5120000,0,0,35.0
```

**Localização:** `/app/data/simulation_run_YYYYMMDD_HHMMSS.csv`

### JSON (Redis/API)
```json
{
  "timestamp": "2025-01-20T10:00:00Z",
  "host_id": "host-1",
  "type": "host",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "latency_ms": 12.5,
    "jitter_ms": 0.3,
    "packet_loss_percent": 0.1,
    "network_rx_bytes": 1024000,
    "network_tx_bytes": 512000,
    "tcp_connections": 42,
    "network_errors": 0,
    "switch_buffer_utilization": 28.5
  }
}
```

### Prometheus Format
```
cpu_usage{host="host-1",type="host",job="simulator"} 45.2
memory_usage{host="host-1",type="host",job="simulator"} 62.1
anomaly_score{host="host-1",job="api"} 0.15
predicted_cpu{host="host-1",job="api"} 47.3
```

---

## 🚀 Deployment e Execução

### Pré-requisitos
- Docker (já instalado na VM)
- Docker Compose
- Acesso SSH à VM do grupo

### Estrutura de Diretórios
```
.
├── docker-compose.yml      # Orquestração
├── .env                    # Variáveis de ambiente
├── nginx.conf             # Configuração proxy
├── prometheus.yml         # Scrape targets
│
├── docker-images/
│   ├── simulator/
│   │   ├── Dockerfile
│   │   └── network_simulator_docker.py
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── train_model.py
│   └── prometheus/
│       └── Dockerfile
│
├── volumes/
│   ├── app_data/          # CSVs e logs
│   ├── prometheus_data/   # Séries temporais
│   ├── grafana_data/      # Dashboards
│   ├── redis_data/        # Cache
│   └── api_models/        # Modelo LSTM + scaler
```

### Inicialização

**1. Login na VM:**
```bash
ssh ginfragrad05@cloudgrad.icmc.usp.br -p <porta>
```

**2. Clonar repositório (se ainda não fez):**
```bash
git clone <repository_url>
cd gemeo-digital-rede
```

**3. Configurar variáveis de ambiente:**
```bash
cat > .env << EOF
SIMULATOR_URL=http://simulator:5001
REDIS_URL=redis://redis:6379/0
DATA_INTERVAL=10
PREDICTION_INTERVAL=60
ANOMALY_THRESHOLD=0.1
EOF
```

**4. Build e iniciar containers:**
```bash
docker-compose up -d --build
```

**5. Verificar status:**
```bash
docker-compose ps
docker-compose logs -f api          # Ver logs API
docker-compose logs -f simulator    # Ver logs Simulador
```

**6. Acessar a solução:**
- Grafana: `VM:porta/grafana/`
- Prometheus: `VM:porta/prometheus/`

### Parar e Remover
```bash
# Parar containers (dados persistem em volumes)
docker-compose down

# Limpar tudo (CUIDADO - deleta volumes)
docker-compose down -v
```

---

## 📚 Treinamento do Modelo LSTM

O modelo LSTM é treinado offline com dados coletados do simulador.

### Executar Treinamento

**1. Coletar dados (6+ horas de simulação):**
```bash
# Via API
POST http://localhost:5000/simulation/start
# Aguardar 6 horas
POST http://localhost:5000/simulation/stop
```

**2. Treinar modelo:**
```bash
# Dentro do container API
docker-compose exec api python train_model.py
```

**Output esperado:**
```
Training model...
Loaded CSV: simulation_run_20250120_100000.csv
Rows: 2160 (6 hours × 6 samples/hour)
Sequences created: 2150
Train/Val split: 1720/430
Model trained successfully!
Saved to: /app/models/network_model_full.h5
Saved scaler to: /app/models/scaler_full.joblib
```

**3. Reiniciar API para carregar novo modelo:**
```bash
docker-compose restart api
```

---

## 🔧 Detalhes Técnicos (Complementares)

### Variáveis de Ambiente Completas

```bash
# Simulador
SIMULATOR_URL=http://simulator:5001
DATA_INTERVAL=10                    # segundos
NUM_HOSTS=6
NUM_SWITCHES=3

# API
REDIS_URL=redis://redis:6379/0
MODEL_PATH=/app/models/
MODEL_NAME=network_model_full.h5
SCALER_NAME=scaler_full.joblib

# ML
ANOMALY_THRESHOLD=0.1               # Contaminação IsolationForest
ANOMALY_STD_THRESHOLD=2.0           # Múltiplos de desvio padrão
TIME_STEPS=10                       # Sequência temporal LSTM

# Prometheus
SCRAPE_INTERVAL=15s
RETENTION=15d

# Grafana
GF_SECURITY_ADMIN_PASSWORD=admin
GF_USERS_ALLOW_SIGN_UP=false
```

### Healthchecks

Cada serviço inclui verificação automática de saúde:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Volumes Persistentes

| Volume | Serviço | Propósito |
|--------|---------|----------|
| `redis_data` | Redis | Persiste dados de cache |
| `prometheus_data` | Prometheus | Séries temporais (TSDB) |
| `grafana_data` | Grafana | Dashboards e configurações |
| `app_data` | API + Simulator | CSVs, logs, dados |
| `api_models` | API | Modelo LSTM e scaler |

---

## 🎓 Como Usar a Solução

### Cenário 1: Monitoramento em Tempo Real
1. Acessar `http://cloudgrad.icmc.usp.br:5191/grafana/`
2. Dashboard mostra métricas reais em tempo real
3. Alertas são disparados quando anomalias detectadas

### Cenário 2: Análise de Anomalias
1. Fazer request: `POST /analysis/anomalies`
2. Sistema retorna anomalias detectadas no lote atual
3. Visualizar scores em dashboard

### Cenário 3: Previsões Futuras
1. Fazer request: `POST /predict`
2. Sistema retorna previsão das 10 métricas para próximo time-step
3. Comparar com valores reais para validação

---

## 📋 Checklist de Entrega

- [x] Arquitetura 100% containerizada com Docker
- [x] Simulador de rede com 6 hosts + 3 switches
- [x] API REST com endpoints de controle
- [x] Detecção de anomalias (Isolation Forest)
- [x] Previsão com LSTM
- [x] Stack de monitoramento (Prometheus + Grafana)
- [x] Cache distribuído (Redis)
- [x] Proxy reverso (Nginx)
- [x] Persistência de dados (volumes Docker)
- [x] README completo com documentação
- [x] Relatório em formato SBC
- [x] Diagrama de arquitetura

---

## 📞 Contato e Dúvidas

Em caso de problemas ou dúvidas:
- **Marcos Vinicius Reballo**: Relatório e desenho de arquitetura
- **Mateus Vargas Saracuza**: Implementação Simulador e coleta de Dados
- **Arthur Azorli**: Treinamento e Implementação do Gêmeo

---

## 📄 Referências

1. Tao et al. (2018). Digital Twin Driven Prognostics and Health Management for Complex Equipment
2. Hochreiter & Schmidhuber (1997). Long Short-Term Memory
3. Liu et al. (2008). Isolation Forest
4. Prometheus Documentation: https://prometheus.io
5. Grafana Documentation: https://grafana.com
6. Docker Documentation: https://docs.docker.com

---

**Versão:** 2.0 (Checkpoint 5-Final)  
**Data:** 22/11/2025  
**Grupo:** 5 - Infraestrutura de Alto Desempenho  
**Instituição:** ICMC - USP
