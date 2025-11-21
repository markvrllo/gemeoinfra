#!/usr/bin/env python3
"""
API Principal do Gêmeo Digital - Versão Dockerizada com IA em Tempo Real
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests
import redis
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import os
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

# Configurações
SIMULATOR_URL = os.getenv('SIMULATOR_URL', 'http://simulator:5001')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')

# --- Definições do Modelo LSTM ---
TIME_STEPS = 10
METRICS = [
    'cpu_usage', 'memory_usage', 'network_rx_bytes', 'network_tx_bytes', 
    'jitter_ms', 'packet_loss_percent', 'latency_ms', 
    'tcp_connections', 'network_errors'
]
MODEL_PATH = '/app/models'
MODEL_NAME = 'network_model_full.h5'
SCALER_NAME = 'scaler_full.joblib'


class DigitalTwinEngine:
    def __init__(self):
        # Redis
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            print("[INFO] Conectado ao Redis")
        except Exception as e:
            print(f"[AVISO] Redis nao disponivel: {e}")
            self.redis_client = None
        
        # ML Anomalia
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.anomaly_scaler = StandardScaler()
        self.anomaly_model_trained = False
        
        # ML Previsão (Carregar Modelo Completo)
        self.prediction_model = None
        self.prediction_scaler = None
        try:
            model_p = os.path.join(MODEL_PATH, MODEL_NAME)
            scaler_p = os.path.join(MODEL_PATH, SCALER_NAME)
            if os.path.exists(model_p) and os.path.exists(scaler_p):
                self.prediction_model = load_model(model_p)
                self.prediction_scaler = joblib.load(scaler_p)
                print(f"[INFO] IA Carregada: {MODEL_NAME}")
            else:
                print(f"[AVISO] Modelos nao encontrados. Execute o treino.")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar IA: {e}")
    
    def get_simulation_data(self):
        try:
            response = requests.get(f'{SIMULATOR_URL}/get_data', timeout=5)
            return response.json() if response.status_code == 200 else None
        except: return None

    def start_simulation(self, duration):
        try:
            return requests.post(f'{SIMULATOR_URL}/start_simulation', json={'duration': duration}, timeout=5).json()
        except Exception as e: return {'error': str(e)}

    def stop_simulation(self):
        try:
            return requests.post(f'{SIMULATOR_URL}/stop_simulation', timeout=5).json()
        except Exception as e: return {'error': str(e)}

    def detect_anomalies(self, data):
        if not data or 'data' not in data: return {'error': 'Sem dados'}
        df = pd.DataFrame(data['data'])
        if 'type' in df.columns: df = df[df['type'] == 'host']
        
        valid_cols = [c for c in METRICS if c in df.columns]
        if not valid_cols: return {'error': 'Colunas invalidas'}
        
        df_processed = df[valid_cols].fillna(0)
        if len(df_processed) < 10: return {'message': 'Dados insuficientes'}

        try:
            if not self.anomaly_model_trained:
                X = self.anomaly_scaler.fit_transform(df_processed)
                self.anomaly_detector.fit(X)
                self.anomaly_model_trained = True
            else:
                X = self.anomaly_scaler.transform(df_processed)
            
            anomalies = self.anomaly_detector.predict(X)
            return {'anomalies_detected': int(np.sum(anomalies == -1))}
        except Exception as e: return {'error': str(e)}

    def predict_full_state(self):
        """Prevê TODAS as métricas do próximo estado"""
        if not self.prediction_model: return None 
        
        raw = self.get_simulation_data()
        if not raw: return None
        
        df = pd.DataFrame(raw['data'])
        
        # Correção de segurança
        if 'type' not in df.columns: 
            return None 
        
        df = df[df['type'] == 'host'] # Filtrar hosts
        
        if not all(col in df.columns for col in METRICS): return None
        sequence = df[METRICS].tail(TIME_STEPS)
        if len(sequence) < TIME_STEPS: return None
        
        try:
            scaled_seq = self.prediction_scaler.transform(sequence)
            input_data = np.array([scaled_seq])
            prediction_scaled = self.prediction_model.predict(input_data, verbose=0)
            prediction_real = self.prediction_scaler.inverse_transform(prediction_scaled)[0]
            
            predictions = {}
            for i, metric in enumerate(METRICS):
                predictions[metric] = max(0, round(float(prediction_real[i]), 2))
                
            return predictions
        except: return None

dt_engine = DigitalTwinEngine()

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gêmeo Digital Completo</title>
        <style>
            body { font-family: sans-serif; margin: 40px; background: #f0f2f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .btn { padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; font-weight: bold; color: white;}
            .btn-run { background: #28a745; }
            .btn-stop { background: #dc3545; }
            .btn-ai { background: #6f42c1; }
            .status-box { background: #e9ecef; padding: 15px; margin-top: 20px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔮 Gêmeo Digital: Previsão Total</h1>
            <div style="text-align:center">
                <button class="btn btn-run" onclick="callAPI('/simulation/start', 'POST', {duration: 172800})">▶ Iniciar</button>
                <button class="btn btn-stop" onclick="callAPI('/simulation/stop', 'POST', {})">⏹ Parar</button>
                <button class="btn btn-ai" onclick="callAPI('/analysis/anomalies', 'POST', {})">🔍 Anomalias</button>
                <button class="btn btn-ai" onclick="callAPI('/predict', 'POST', {})">🧠 Ver Previsão (JSON)</button>
            </div>
            <div id="output" class="status-box">Aguardando comando...</div>
        </div>
        <script>
            async function callAPI(url, method, body) {
                document.getElementById('output').innerHTML = "Processando...";
                try {
                    const res = await fetch(url, {
                        method: method,
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(body)
                    });
                    const data = await res.json();
                    document.getElementById('output').innerHTML = JSON.stringify(data, null, 2);
                } catch (e) {
                    document.getElementById('output').innerHTML = "Erro: " + e.message;
                }
            }
        </script>
    </body>
    </html>
    """)

@app.route('/health', methods=['GET'])
def health(): return jsonify({'status': 'ok'})

@app.route('/simulation/start', methods=['POST'])
def start(): return jsonify(dt_engine.start_simulation(request.json.get('duration', 300)))

@app.route('/simulation/stop', methods=['POST'])
def stop(): return jsonify(dt_engine.stop_simulation())

@app.route('/analysis/anomalies', methods=['POST'])
def anomalies(): return jsonify(dt_engine.detect_anomalies(dt_engine.get_simulation_data()))

@app.route('/predict', methods=['POST'])
def predict(): 
    result = dt_engine.predict_full_state()
    if result: return jsonify(result)
    return jsonify({'error': 'Não foi possível gerar previsão (falta de dados ou modelo)'}), 500

@app.route('/metrics')
def metrics():
    final_output = ""
    try:
        sim_response = requests.get(f'{SIMULATOR_URL}/metrics', timeout=2)
        if sim_response.status_code == 200: final_output += sim_response.text
    except: final_output += "# Simulator metrics unavailable\n"

    predictions = dt_engine.predict_full_state()
    if predictions:
        final_output += "\n# PREDICTIONS FROM DIGITAL TWIN AI (LSTM)\n"
        for metric_name, value in predictions.items():
            final_output += f"# HELP predicted_{metric_name} AI Predicted value for {metric_name}\n"
            final_output += f"# TYPE predicted_{metric_name} gauge\n"
            final_output += f"predicted_{metric_name} {value}\n"

    return final_output, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
