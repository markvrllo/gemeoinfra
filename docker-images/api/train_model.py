#!/usr/bin/env python3
"""
Script de Treinamento do Gêmeo Digital (LSTM Multi-Output)

Treina um modelo para prever TODAS as métricas do próximo estado
com base no histórico.
"""

import pandas as pd
import numpy as np
import glob
import os
import joblib
import logging
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Configuração de logging simples
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

# --- 1. Definições ---
TIME_STEPS = 10 

# Lista de TODAS as métricas que queremos prever (Ordem é importante!)
METRICS = [
    'cpu_usage', 
    'memory_usage', 
    'network_rx_bytes', 
    'network_tx_bytes', 
    'jitter_ms', 
    'packet_loss_percent', 
    'latency_ms', 
    'tcp_connections', 
    'network_errors'
]

DATA_PATH = '/app/data'
MODEL_PATH = '/app/models'
MODEL_NAME = 'network_model_full.h5'
SCALER_NAME = 'scaler_full.joblib' 

def find_latest_csv(path):
    """Encontra o ficheiro CSV mais recente na pasta de dados."""
    logging.info(f"Procurando por CSVs em {path}...")
    list_of_files = glob.glob(f'{path}/simulation_run_*.csv')
    if not list_of_files:
        logging.error(f"Nenhum ficheiro CSV encontrado em {path}. Execute a simulação primeiro.")
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    logging.info(f"Ficheiro de dados encontrado: {latest_file}")
    return latest_file

def load_data(filepath):
    """Carrega e pré-processa os dados do CSV."""
    df = pd.read_csv(filepath)
    
    # O simulador mistura dados de host e switch, vamos filtrar
    df_hosts = df[df['type'] == 'host'].copy()
    
    # Garantir que colunas existem
    for col in METRICS:
        if col not in df_hosts.columns:
            logging.error(f"Coluna '{col}' não encontrada no CSV.")
            return None
    
    # Selecionar apenas as métricas
    df_features = df_hosts[METRICS].dropna()
    logging.info(f"{len(df_features)} amostras de dados de host encontradas.")
    return df_features

def create_sequences(data, time_steps):
    """Transforma os dados em sequências para a LSTM."""
    Xs, ys = [], []
    for i in range(len(data) - time_steps):
        Xs.append(data[i:(i + time_steps)])
        ys.append(data[i + time_steps]) # O alvo é a linha inteira de métricas!
    return np.array(Xs), np.array(ys)

def build_model(input_shape, output_units):
    """Cria a arquitetura do modelo LSTM."""
    model = Sequential()
    model.add(LSTM(units=64, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=64))
    model.add(Dropout(0.2))
    model.add(Dense(units=output_units)) 
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    logging.info("Modelo Multi-Output criado.")
    return model

def main():
    # 1. Carregar
    latest_csv = find_latest_csv(DATA_PATH)
    if not latest_csv: return
    data = load_data(latest_csv)
    if data is None or len(data) < (TIME_STEPS + 50): 
        logging.error(f"Dados insuficientes para treino. Mínimo: {TIME_STEPS + 50}. Encontrado: {len(data)}")
        return

    # 2. Escalonar
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # 3. Sequenciar
    X, y = create_sequences(scaled_data, TIME_STEPS)
    
    n_features = X.shape[2]
    logging.info(f"X shape: {X.shape}, y shape: {y.shape}")

    # 4. Treinar
    model = build_model((TIME_STEPS, n_features), n_features)
    
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    logging.info("Iniciando treino do modelo...")
    history = model.fit(
        X, y,
        epochs=50, 
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        shuffle=False
    )
    
    logging.info("Treino concluído.")
    
    # 5. Salvar
    if not os.path.exists(MODEL_PATH): os.makedirs(MODEL_PATH)
    
    model_save_path = os.path.join(MODEL_PATH, MODEL_NAME)
    scaler_save_path = os.path.join(MODEL_PATH, SCALER_NAME)

    model.save(model_save_path)
    joblib.dump(scaler, scaler_save_path)
    
    final_loss = history.history['val_loss'][-1]
    logging.info(f"Perda (MSE) final no conjunto de validação: {final_loss}")
    logging.info(f"✅ [SUCESSO] Modelo completo salvo com sucesso!")

if __name__ == "__main__":
    main()
