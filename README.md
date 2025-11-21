[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Yp5Hxsev)

# Acesso à VM

Abaixo, seguem informações de login e senha para que o grupo possa acessar a VM disponível para a realização do projeto.

**login: ginfragrad05**

**senha: Lq4xzVR4**
 
O acesso via SSH pode ser feito seguindo:

```bash
ssh <login>@cloudgrad.icmc.usp.br -p porta
```

Com esta VM, o Docker pode ser utilizado, junto da criação do projeto da disciplina. 

O login do seu grupo tem poder de root, de modo que vocês podem instalar e configurar o que precisam. O Docker já está configurado para uso e não precisa ser instalado. Em caso de qualquer dúvida ou dificuldade de acesso, consultar o professor da disciplina: jcezar@icmc.usp.br

# Mapeamento de Portas (Exemplo)	

| Local (VM)    | Remota (WWW) - Porta Web   |
|---------------|----------------------------|
| 5191          | 5191                       |

Consulte a porta-web correspondente ao seu grupo na planilha com informações do grupo lá no moodle.

# Acesso WEB	
http://cloudgrad.icmc.usp.br:porta-web	


# Gêmeos Digitais - Sumário

Segundo a wikipedia, um gêmeo digital é uma representação virtual detalhada de um objeto, sistema ou processo físico, criada para simular seu comportamento e características em tempo real a partir de dados coletados via sensores e dispositivos IoT. A principal função é espelhar o ciclo de vida do ativo físico, permitindo análise, monitoramento, simulação e otimização contínua.

## Definição e Características

Ainda, segundo o instituto de Pesquisas CESAR, podemos definir as características de gêmeos digitais como integralizadores de dados de múltiplas fontes, para criar uma cópia digital dinâmica do ativo real, atualizada continuamente pelos fluxos de dados dos sensores. Vão além de simples modelos 3D, pois combinam informações em tempo real, modelagem analítica (IA ou machine learning), e exibem o estado atual, previsão de falhas, manutenção preditiva e simulações de cenários.

O conceito pode englobar tanto produtos (máquinas, edifícios, veículos) quanto processos (linhas de produção, cadeias logísticas) e pode ser aplicado em diversos setores industriais e de serviços.

# Introdução do Projeto

O presente documento apresenta a estruturação e o desenvolvimento dos checkpoints 1 e 2 do projeto de Gêmeo Digital focado no monitoramento de desempenho de rede.

Um Gêmeo Digital é uma representação virtual de um sistema físico que utiliza dados em tempo real para simular e monitorar comportamentos, permitindo análises preditivas e otimizações sem interferir no sistema real. No contexto específico de redes, um Network Digital Twin (NDT) representa uma plataforma avançada para emulação de rede, servindo como ferramenta para planejamento de cenários, análise de impacto e gestão de mudanças.

---

## Checkpoint 1 - Planejamento

### Objetivos e Escopo do Projeto

O Checkpoint 1 estabelece os fundamentos conceituais e técnicos do projeto, definindo objetivos claros para o desenvolvimento de um gêmeo digital focado no monitoramento de desempenho de rede. Este escopo específico permite uma abordagem direcionada para métricas críticas como latência, throughput, perda de pacotes e utilização de banda.

---

### Arquitetura Proposta

A arquitetura do gêmeo digital será estruturada seguindo os princípios de sistemas distribuídos de alto desempenho, incorporando as seguintes camadas:

#### 1. Camada de Coleta de Dados

- **Prometheus:** Sistema de monitoramento e alerta open-source para coleta de métricas de rede.
- **SNMP Exporter:** Extração de dados de dispositivos de rede via protocolo SNMP.
- **Node Exporter:** Coleta métricas do sistema operacional e hardware do servidor.

#### 2. Camada de Processamento

- **Docker:** Containerização dos componentes para portabilidade e isolamento.
- **Python com Flask:** Desenvolvimento de APIs para interação com o gêmeo digital.
- **Bibliotecas de ML:** Para modelagem preditiva (LSTM, scikit-learn).

#### 3. Camada de Visualização

- **Grafana:** Dashboards para visualização de métricas em tempo real.
- **Interface Web:** Dashboard personalizado para controle do gêmeo digital.

#### 4. Camada de Modelagem

- **Modelo Matemático:** Baseado em séries temporais para análise de padrões de tráfego.
- **Modelos de ML:** Algoritmos preditivos para detecção de anomalias e previsão de desempenho.

#### Componentes de Infraestrutura

- **DNS e Service Discovery**

A implementação utilizará o DNS interno do Docker para comunicação entre serviços na mesma rede. Serão configurados nomes de domínio amigáveis para acesso às APIs de simulação, com possível implementação de proxy reverso para flexibilidade adicional.

- **Middleware de Comunicação**

Haverá integração de sistemas de mensageria como RabbitMQ ou Apache Kafka para facilitar a comunicação entre componentes distribuídos. O middleware também implementará camadas de autenticação para controle de acesso às APIs.

- **Virtualização e Containerização**
A utilização do Docker permitirá a virtualização de recursos, possibilitando deployment em diferentes ambientes (desenvolvimento, teste, produção). A containerização oferece vantagens como isolamento, portabilidade e consistência de ambiente.

Com base no tema específico do nosso grupo, o gêmeo digital inicialmente focará nas seguintes métricas de desempenho de rede:
---

### Métricas de Rede a Serem Monitoradas

- **Latência de Rede:** Tempo de resposta entre origem e destino.
- **Throughput:** Taxa de transferência de dados efetiva.
- **Perda de Pacotes:** Percentual de pacotes perdidos durante a transmissão.
- **Utilização de Banda:** Percentual de capacidade utilizada em interfaces de rede.
- **Jitter:** Variação no tempo de chegada de pacotes.
- **Qualidade de Serviço (QoS):** Métricas de priorização de tráfego.

---

### Tecnologias e Ferramentas Selecionadas

#### Stack de Monitoramento

- **Prometheus + Grafana:** Stack consolidado para monitoramento e visualização.
- **ElasticSearch:** Para armazenamento e busca de logs de rede.
- **InfluxDB:** Banco de dados otimizado para séries temporais.

#### Desenvolvimento e Deploy

- **Docker Compose:** Orquestração de containers para desenvolvimento.
- **Kubernetes:** Para deployment em produção com alta disponibilidade.
- **Python Flask:** Framework web para APIs RESTful.

#### Modelagem Matemática Preliminar

O modelo matemático inicial irá basear-se em análise de séries temporais para capturar padrões de comportamento da rede. O hardware em

Alguns exemplos que podemos citar são:
- **Modelo ARIMA:** Para previsão de métricas de tráfego.
- **Redes Neurais LSTM:** Para detecção de anomalias em padrões complexos.
- **Algoritmos de Regressão:** Para correlação entre diferentes métricas.

---

### Plano de Implementação

**Fase 1: Setup da Infraestrutura**
- Configuração do ambiente Docker.
- Deploy inicial do Prometheus e Grafana.
- Configuração de coleta básica de métricas.

**Fase 2: Desenvolvimento do Gêmeo Digital**
- Implementação das APIs em Flask.
- Desenvolvimento dos modelos de simulação.
- Integração com sistemas de coleta de dados.

**Fase 3: Validação e Testes**
- Testes de carga e performance.
- Validação dos modelos preditivos.
- Ajustes de configuração e otimização.

---

# Checkpoint 2 - Detalhamento da Possível Arquitetura do Sistema

## 🎯 Segundo Checkpoint - Arquitetura Detalhada

### Objetivo
Avaliar o andamento da arquitetura proposta para o gêmeo digital, com foco na infraestrutura considerada e apresentação de diagrama detalhado dos serviços em utilização e comunicação entre eles.

### Entregáveis Obrigatórios
- ✅ **README atualizado** com nova seção de arquitetura de infraestrutura
- ✅ **Diagrama de arquitetura** ilustrando serviços e comunicação
- ✅ **Tag no GitHub** marcando entrega (`checkpoint2`)
- ✅ **Apresentação** recapitulando proposta e infraestrutura de suporte

---

## 🏗️ Arquitetura de Infraestrutura do Sistema

### Visão Geral
O Gêmeo Digital para Monitoramento de Desempenho de Rede é implementado seguindo uma arquitetura de **microserviços distribuídos containerizados**, garantindo escalabilidade, manutenibilidade e isolamento entre componentes. O **diagrama abaixo poderá ser modificado ao longo do projeto.**

### Diagrama da Arquitetura

![Digrama Inicial da Arquitetura](images/DT_v0_network_traffic.png)

---

## 🔧 Componentes da Infraestrutura

### 1. Camada de Apresentação
#### Interface Web Dashboard
- **Tecnologia**: HTML5, CSS3, JavaScript (Vue.js)
- **Porta**: 5191 (mapeada para acesso externo)
- **Função**: Interface principal para usuários finais
- **Comunicação**: API REST com backend Flask

#### Grafana Dashboards
- **Container**: `grafana/grafana:latest`
- **Porta**: 3000 (interna), 5191 (externa via proxy)
- **Função**: Visualização avançada de métricas e alertas
- **Dados**: Conecta diretamente ao Prometheus via DataSource

### 2. Camada de API
#### Digital Twin API
- **Tecnologia**: Python Flask + gunicorn
- **Container**: Custom Python image
- **Porta**: 5000 (interna)
- **Endpoints Principais**:
  - `GET /api/metrics` - Métricas atuais de rede
  - `POST /api/simulate` - Execução de simulações
  - `GET /api/anomalies` - Detecção de anomalias
  - `POST /api/predict` - Análises preditivas

#### Nginx Load Balancer
- **Container**: `nginx:alpine`
- **Porta**: 80 (interna), 5191 (externa)
- **Função**: Proxy reverso, SSL termination, load balancing
- **Configuração**: Round-robin para múltiplas instâncias da API

### 3. Camada de Processamento
#### ML Engine (Machine Learning)
- **Algoritmos Implementados**:
  - **Isolation Forest**: Detecção de anomalias em tempo real
  - **LSTM Networks**: Previsão de padrões de tráfego
  - **ARIMA Models**: Análise de séries temporais
- **Bibliotecas**: scikit-learn, tensorflow, pandas, numpy
- **Processamento**: Assíncrono com Celery workers

#### Network Simulator
- **Tecnologia**: Mininet + Python
- **Função**: Simulação de cenários de rede
- **Cenários Suportados**:
  - Testes de carga
  - Simulação de falhas
  - Análise de capacidade
  - Otimização de rotas

### 4. Camada de Coleta
#### Prometheus
- **Container**: `prom/prometheus:latest`
- **Porta**: 9090 (interna)
- **Configuração**: Scraping interval de 15 segundos
- **Targets**:
  - SNMP Exporter (dispositivos de rede)
  - Node Exporter (métricas de sistema)
  - API própria (métricas customizadas)

#### SNMP Exporter
- **Container**: `prom/snmp-exporter:latest`
- **Porta**: 9116 (interna)
- **Protocolo**: SNMP v2c/v3
- **MIBs Suportadas**: IF-MIB, HOST-MIB, ENTITY-MIB
- **Dispositivos Monitorados**:
  - Switches de rede
  - Roteadores
  - Access Points
  - Firewalls

#### Node Exporter
- **Container**: `prom/node-exporter:latest`
- **Porta**: 9100 (interna)
- **Métricas Coletadas**:
  - CPU usage e load average
  - Memória RAM e swap
  - I/O de disco
  - Interface de rede
  - Processos do sistema

### 5. Camada de Dados
#### Redis Cache
- **Container**: `redis:alpine`
- **Porta**: 6379 (interna)
- **Função**: Cache de consultas frequentes, sessões de usuário
- **TTL**: 300 segundos para métricas, 3600 para análises

#### Time Series Database
- **Implementação**: Prometheus TSDB integrado
- **Retenção**: 30 dias de dados históricos
- **Compressão**: Automática para otimização de storage
- **Backup**: Snapshots diários para storage externo

#### Backup Storage
- **Local**: Volume Docker persistente
- **Remoto**: Sincronização com storage da VM
- **Frequência**: Backup incremental a cada 6 horas
- **Retenção**: 90 dias de backups

---

## 🔄 Comunicação Entre Serviços

### Protocolos Utilizados
- **HTTP/HTTPS**: Comunicação API REST
- **gRPC**: Comunicação interna entre microserviços críticos
- **WebSockets**: Streaming de métricas em tempo real
- **MQTT**: Telemetria de dispositivos IoT (futuro)

### Service Discovery
- **Implementação**: Docker Compose DNS
- **Resolução**: Nome do container → IP interno
- **Load Balancing**: Nginx upstream configuration
- **Health Checks**: Endpoints `/health` em todos os serviços

### Fluxo de Dados
1. **Coleta**: Dispositivos → SNMP Exporter → Prometheus → TSDB
2. **Processamento**: API → ML Engine → Redis Cache
3. **Visualização**: Grafana ← Prometheus ← TSDB
4. **Interface**: Web Dashboard → API → Múltiplas fontes

---

## 🚀 Deployment e Orquestração

```
volumes:
  prometheus_data:
  grafana_data:
```
---

## 📊 Monitoramento da Infraestrutura

### Métricas de Sistema
- **Disponibilidade**: Uptime de cada serviço
- **Performance**: Latência de APIs, throughput de dados
- **Recursos**: CPU, memória, storage por container
- **Rede**: Bandwidth utilizado, conexões ativas

### Alertas Configurados
- **API Response Time** > 500ms
- **Container Memory** > 80%
- **Disk Space** < 10% livre
- **Network Anomaly Score** > 0.8

### Dashboards Disponíveis
1. **Overview**: Status geral do sistema
2. **Network Performance**: Métricas de rede em tempo real
3. **ML Insights**: Resultados dos algoritmos de ML
4. **Infrastructure**: Saúde dos containers e recursos

---

## 🔒 Segurança e Compliance

### Medidas de Segurança
- **Autenticação**: JWT tokens para APIs
- **Autorização**: Role-based access control (RBAC)
- **Comunicação**: TLS 1.3 para tráfego externo
- **Containers**: Non-root users, read-only filesystems
- **Network**: Docker networks isoladas por função

### Backup e Recovery
- **RTO (Recovery Time Objective)**: < 30 minutos
- **RPO (Recovery Point Objective)**: < 1 hora
- **Disaster Recovery**: Procedimentos documentados
- **Testing**: Restore tests mensais

---

## 📈 Escalabilidade e Performance

### Scaling Horizontal
- **API**: Auto-scaling baseado em CPU/memória
- **Workers**: Celery workers dinâmicos
- **Database**: Sharding por timestamp (futuro)
- **Cache**: Redis Cluster (produção)

### Otimizações
- **Connection Pooling**: Para todas as conexões de DB
- **Caching Strategy**: Multi-layer (Redis + application)
- **Data Compression**: Gzip para APIs, built-in para TSDB
- **Resource Limits**: Definidos para todos os containers

---

## 🎯 Métricas de Rede Monitoradas

### Métricas Principais
- **Latência**: Round-trip time, jitter
- **Throughput**: Bits/segundo por interface
- **Perda de Pacotes**: Percentual de packet loss
- **Utilização**: Bandwidth utilizado vs disponível
- **Qualidade de Serviço**: QoS metrics por classe

### Métricas Avançadas
- **TCP Connection States**: Established, time-wait, etc.
- **Buffer Utilization**: Switch/router buffer usage
- **Error Rates**: CRC errors, frame errors
- **Routing Metrics**: Convergence time, path changes

---

## 🧪 Testes e Validação

### Ambiente de Testes
- **Unit Tests**: 95% code coverage
- **Integration Tests**: End-to-end scenarios
- **Load Tests**: 1000+ concurrent users
- **Chaos Engineering**: Failure injection tests

### Cenários de Simulação
1. **Normal Operation**: Baseline performance
2. **High Load**: 10x normal traffic
3. **Network Failure**: Link down scenarios
4. **Resource Exhaustion**: CPU/memory limits
5. **Security Attacks**: DDoS simulation

---

*Este documento representa a arquitetura detalhada do Gêmeo Digital para Monitoramento de Desempenho de Rede, desenvolvido como parte da disciplina de Infraestrutura de Alto Desempenho, SSC0954 do BSI025.*