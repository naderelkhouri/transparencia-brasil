"""
Testes automatizados da API REST de Transparência de Gastos Públicos.
"""

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["banco_analitico"] == "conectado"


def test_api_web_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "Transparência Brasil" in response.text


def test_api_resumo_nacional():
    response = client.get("/api/v1/resumo?ano=2026")
    assert response.status_code == 200
    data = response.json()
    assert "gasto_efetivo_nacional" in data
    assert "total_pago_liquido" in data
    assert "total_transferencias_intergovernamentais" in data
    assert "total_alertas_corrupcao" in data
    assert data["total_alertas_corrupcao"] >= 3
    assert data["valor_sob_alerta_corrupcao"] > 0
    # Verifica que gasto efetivo não inclui transferências
    assert data["gasto_efetivo_nacional"] > 0
    assert data["total_transferencias_intergovernamentais"] > 0


def test_api_alertas_corrupcao():
    response = client.get("/api/v1/alertas-corrupcao?ano=2026")
    assert response.status_code == 200
    alertas = response.json()
    assert len(alertas) >= 3
    # Verifica presença de tipos de risco graves
    tipos = [a["tipo_risco"] for a in alertas]
    assert "EMPRESA_INIDONEA_CEIS" in tipos
    assert "SOBREPRECO_ATIPICO" in tipos
    assert "FRACIONAMENTO_ILEGAL" in tipos
    assert any("🚨" in a["motivo_corrupcao"] for a in alertas)


def test_api_ranking_orgaos():
    response = client.get("/api/v1/orgaos?ano=2026&limite=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    primeiro = data[0]
    assert "codigo" in primeiro
    assert "nome" in primeiro
    assert "total_pago" in primeiro


def test_api_rastreabilidade_sucesso():
    doc_id = "2026OB800142"
    response = client.get(f"/api/v1/rastreabilidade/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["documento"]["numero"] == doc_id
    assert "auditoria_proveniencia" in data
    assert "url_oficial" in data["auditoria_proveniencia"]


def test_api_rastreabilidade_nao_encontrado():
    response = client.get("/api/v1/rastreabilidade/DOC_INEXISTENTE_999")
    assert response.status_code == 404


def test_api_siconfi_municipios():
    response = client.get("/api/v1/siconfi/municipios?ano=2026")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    sp = next(m for m in data if m["municipio"] == "São Paulo")
    assert sp["gasto_per_capita"] > 0
    assert sp["populacao_ibge"] > 10_000_000


def test_api_pncp_contratos():
    response = client.get("/api/v1/pncp/contratos?ano=2026")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "objeto" in data[0]
    assert "fornecedor_cnpj" in data[0]
