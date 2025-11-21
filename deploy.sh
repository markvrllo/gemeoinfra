#!/bin/bash
set -e

echo "🚀 Deploy do Gêmeo Digital Containerizado"
echo "========================================"

# 1. Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está disponível"
    exit 1
fi

# 2. Criar diretórios necessários
echo "📁 Garantindo estrutura de diretórios..."
mkdir -p {data,logs,models,config,web-interface}

# 3. Parar tudo (Limpeza)
echo "🛑 Parando containers antigos..."
docker compose down --remove-orphans 2>/dev/null || true

# 4. Construir Imagens
echo "🔨 Construindo imagens Docker..."
docker compose build

# 5. Iniciar
echo "🌟 Iniciando serviços..."
docker compose up -d

# 6. Aguardar
echo "⏳ Aguardando inicialização (20 segundos)..."
sleep 20

# 7. Relatório Final
echo ""
echo "🔍 Status Final dos Serviços:"
docker compose ps

echo ""
echo "🎉 Deploy concluído com sucesso! O script encerrou."
echo "========================================"
echo "📊 Aceda em: http://andromeda.lasdpc.icmc.usp.br:5385/"
echo ""

# Forçar saída com sucesso
exit 0
