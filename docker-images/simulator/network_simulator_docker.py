#!/usr/bin/env python3
"""
Simulador de Rede Dockerizado - Versão Final (CORRIGIDA)
Corrige o bug onde apenas os Switches apareciam no Grafana.
"""

import time
import json
import random
import threading
import requests
import psutil
from datetime import datetime
from flask import Flask, jsonify, request
import pandas as pd
import redis
import os

app = Flask(__name__)

class DockerNetworkSimulator:
    def __init__(self):
        self.is_running = False
        self.csv_filename = None
        self.csv_header_written = False
        self.simulation_config = {
            'hosts': 6,
            'switches': 3,
            'data_interval': 10
        }
        
        try:
            self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
            self.redis_client.ping()
            print("[INFO] Conectado ao Redis")
        except Exception as e:
            self.redis_client = None
            print(f"[AVISO] Redis nao disponivel: {e}")
    
    def simulate_host_metrics(self, host_id, timestamp):
        base_cpu = 20 + (host_id * 5) + random.uniform(-10, 15)
        base_memory = 45 + (host_id * 3) + random.uniform(-8, 12)
        base_latency = 1 + (abs(host_id - 3) * 2) + random.uniform(0, 5)
        jitter_ms = base_latency * random.uniform(0.05, 0.2)
        network_load = random.uniform(100000, 5000000)
        
        return {
            'timestamp': timestamp, 'type': 'host', 'host': f'h{host_id}', 'switch': None,
            'cpu_usage': max(0, min(100, base_cpu)), 'memory_usage': max(0, min(100, base_memory)),
            'latency_ms': base_latency, 'jitter_ms': max(0.1, jitter_ms),
            'packet_loss_percent': random.uniform(0, 2), 'tcp_connections': random.randint(10, 500),
            'network_rx_bytes': int(network_load * random.uniform(0.7, 1.3)),
            'network_tx_bytes': int(network_load * random.uniform(0.8, 1.2)),
            'network_errors': random.randint(0, 5),
            'buffer_utilization': None, 'total_flows': None
        }
    
    def simulate_switch_metrics(self, switch_id, timestamp):
        return {
            'timestamp': timestamp, 'type': 'switch', 'host': None, 'switch': f's{switch_id}',
            'cpu_usage': None, 'memory_usage': None, 'latency_ms': None, 'jitter_ms': None,
            'packet_loss_percent': None, 'tcp_connections': None, 'network_rx_bytes': None,
            'network_tx_bytes': None, 'network_errors': None,
            'buffer_utilization': random.uniform(10, 70), 'total_flows': random.randint(50, 500)
        }

    def write_batch_to_csv(self, batch):
        if not self.csv_filename: return
        try:
            df = pd.DataFrame(batch)
            if not self.csv_header_written:
                df.to_csv(self.csv_filename, index=False, mode='w'); self.csv_header_written = True
            else: df.to_csv(self.csv_filename, index=False, mode='a', header=False)
        except: pass

    def run_simulation(self, duration_seconds=300):
        self.csv_filename = f'/app/data/simulation_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        self.csv_header_written = False
        print(f"[INFO] Iniciando simulacao. Dados: {self.csv_filename}")
        self.is_running = True
        start_time = time.time()
        
        while self.is_running and (time.time() - start_time) < duration_seconds:
            timestamp = datetime.now().isoformat()
            batch = []
            # Gerar Hosts
            for i in range(1, self.simulation_config['hosts'] + 1):
                batch.append(self.simulate_host_metrics(i, timestamp))
            # Gerar Switches
            for i in range(1, self.simulation_config['switches'] + 1):
                batch.append(self.simulate_switch_metrics(i, timestamp))
            
            self.write_batch_to_csv(batch)
            
            # --- CORREÇÃO AQUI ---
            # Enviar TODOS os itens do lote para o Redis, não apenas o último
            if self.redis_client:
                try:
                    for item in batch:
                        self.redis_client.lpush('network_metrics', json.dumps(item))
                    # Manter apenas os últimos 500 itens para não encher a memória do Redis
                    self.redis_client.ltrim('network_metrics', 0, 500)
                except: pass
            
            print(f"[INFO] Lote de {len(batch)} pontos gerado.")
            time.sleep(self.simulation_config['data_interval'])
        
        self.is_running = False

simulator = DockerNetworkSimulator()

@app.route('/health')
def health(): return jsonify({'status': 'healthy', 'simulation_running': simulator.is_running})

@app.route('/start_simulation', methods=['POST'])
def start():
    if simulator.is_running: return jsonify({'error': 'Running'}), 400
    threading.Thread(target=simulator.run_simulation, args=(request.json.get('duration', 300),), daemon=True).start()
    return jsonify({'message': 'Simulação iniciada'})

@app.route('/stop_simulation', methods=['POST'])
def stop(): simulator.is_running = False; return jsonify({'message': 'Simulação parada', 'file': simulator.csv_filename})

@app.route('/simulation_status')
def status(): return jsonify({'running': simulator.is_running})

@app.route('/get_data')
def get():
    if not simulator.redis_client: return jsonify({'error': 'No Redis'}), 500
    try: 
        # Ler mais dados para garantir que apanhamos hosts e switches
        raw = simulator.redis_client.lrange('network_metrics', 0, 50)
        return jsonify({'data': [json.loads(i) for i in raw]})
    except: return jsonify({'error': 'Redis error'}), 500

@app.route('/metrics')
def metrics():
    txt = ""
    txt += f"network_simulation_active {1 if simulator.is_running else 0}\n"
    if not simulator.redis_client: return txt, 200, {'Content-Type': 'text/plain'}
    
    try:
        # Ler itens suficientes para cobrir todos os devices (9 devices)
        # Lendo 50 para garantir segurança
        data_list = [json.loads(i) for i in simulator.redis_client.lrange('network_metrics', 0, 50)]
        
        # Dicionário para evitar duplicados (usar o timestamp mais recente de cada host)
        processed_hosts = set()
        processed_switches = set()

        for d in data_list:
            if d.get('type') == 'host':
                h = d['host']
                if h not in processed_hosts:
                    l = f'host="{h}", job="gemeo-simulator"'
                    txt += f'cpu_usage{{{l}}} {d["cpu_usage"]}\n'
                    txt += f'memory_usage{{{l}}} {d["memory_usage"]}\n'
                    txt += f'latency_ms{{{l}}} {d["latency_ms"]}\n'
                    txt += f'jitter_ms{{{l}}} {d["jitter_ms"]}\n'
                    txt += f'packet_loss_percent{{{l}}} {d["packet_loss_percent"]}\n'
                    txt += f'network_rx_bytes{{{l}}} {d["network_rx_bytes"]}\n'
                    txt += f'network_tx_bytes{{{l}}} {d["network_tx_bytes"]}\n'
                    txt += f'tcp_connections{{{l}}} {d["tcp_connections"]}\n'
                    txt += f'network_errors{{{l}}} {d["network_errors"]}\n'
                    processed_hosts.add(h)
            
            elif d.get('type') == 'switch':
                s = d['switch']
                if s not in processed_switches:
                    l = f'switch="{s}", job="gemeo-simulator"'
                    txt += f'switch_buffer_utilization{{{l}}} {d["buffer_utilization"]}\n'
                    processed_switches.add(s)

    except Exception as e: txt += f"# Error processing metrics: {str(e)}\n"
    return txt, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__': app.run(host='0.0.0.0', port=5001)
