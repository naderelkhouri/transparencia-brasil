#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "========================================================================"
echo "🏛️  TRANSPARÊNCIA BRASIL — PLATAFORMA DE GASTOS PÚBLICOS"
echo "========================================================================"

if [ ! -d ".venv" ]; then
    echo "⚡ Criando ambiente virtual com UV e instalando dependências..."
    uv venv --python 3.12 .venv
    uv pip install --python .venv/bin/python -e .
fi

echo "🔄 Verificando e atualizando dados analíticos (Bronze ➔ Silver ➔ Gold)..."
.venv/bin/python packages/pipeline/run_pipeline.py

echo ""
echo "🚀 Iniciando servidor web e API em http://localhost:8000"
echo "   • Painel Cidadão & Auditoria:  http://localhost:8000"
echo "   • Documentação OpenAPI/Docs:    http://localhost:8000/docs"
echo "========================================================================"
echo "Pressione Ctrl+C para encerrar o servidor."
echo ""

exec .venv/bin/uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
