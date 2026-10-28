"""
API REST Oficial da Plataforma de Transparência de Gastos Públicos Brasileiros.
Arquitetura de alta performance com FastAPI, DuckDB e documentação OpenAPI 3.1.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from packages.pipeline.gold_engine import GoldAnalyticsEngine
from packages.pipeline.extractors.siconfi_extractor import ExtratorSiconfi
from packages.pipeline.extractors.pncp_extractor import ExtratorPNCP
from packages.pipeline.run_pipeline import executar_pipeline

app = FastAPI(
    title="Plataforma de Transparência - Gastos Públicos do Brasil",
    description=(
        "API oficial para consulta de despesas públicas, execução orçamentária (Lei 4.320/64), "
        "indicadores fiscais subnacionais (SICONFI), contratações públicas (PNCP) "
        "e rastreabilidade até o documento oficial original."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS liberado para frontend local e produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir Frontend Web Estático
static_dir = Path("/home/nader/transparencia-brasil/apps/web/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", include_in_schema=False)
def index_web():
    """Entrega o dashboard web interativo da plataforma."""
    html_file = static_dir / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"mensagem": "Plataforma Transparência Brasil - API ativa. Acesse /docs para documentação."}

engine = GoldAnalyticsEngine()
extrator_siconfi = ExtratorSiconfi()
extrator_pncp = ExtratorPNCP()


@app.get("/health", tags=["Sistema"])
def health_check():
    """Verifica a integridade do serviço e da base analítica."""
    try:
        count = engine.conn.execute("SELECT COUNT(*) FROM fato_despesa_unificada").fetchone()[0]
        return {
            "status": "online",
            "banco_analitico": "conectado",
            "registros_carregados": count,
        }
    except Exception as e:
        return {"status": "degradado", "erro": str(e)}


@app.get("/api/v1/resumo", tags=["Métricas Nacionais"])
def obter_resumo(ano: int = Query(2026, description="Ano do exercício orçamentário")):
    """
    Retorna o resumo nacional orçamentário do ano.
    Separa estritamente Empenhado, Liquidado e Pago Líquido,
    além de calcular o Gasto Efetivo Nacional (subtraindo repasses intergovernamentais).
    """
    return engine.obter_resumo_nacional(ano=ano)


@app.get("/api/v1/despesas", tags=["Consultas Granulares"])
def listar_despesas(
    ano: int = Query(2026, description="Ano do exercício"),
    orgao: Optional[str] = Query(None, description="Código do órgão superior (ex: 36000 para Saúde)"),
    funcao: Optional[str] = Query(None, description="Função governamental (ex: 'Saúde', 'Educação')"),
    fase: Optional[str] = Query(None, description="Fase contábil: 'DOTACAO', 'EMPENHO', 'LIQUIDACAO', 'PAGAMENTO'"),
    busca: Optional[str] = Query(None, description="Termo livre (favorecido, número de documento, etc.)"),
    limite: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Consulta avançada de despesas com filtros múltiplos e paginação."""
    return engine.buscar_despesas(
        ano=ano,
        orgao=orgao,
        funcao=funcao,
        fase=fase,
        termo_busca=busca,
        limite=limite,
        offset=offset,
    )


@app.get("/api/v1/orgaos", tags=["Rankings & Agregações"])
def listar_ranking_orgaos(
    ano: int = Query(2026, description="Ano do exercício"),
    limite: int = Query(10, ge=1, le=50),
):
    """Retorna ranking dos ministérios e órgãos superiores com maior volume pago."""
    return engine.obter_ranking_orgaos(ano=ano, limite=limite)


@app.get("/api/v1/funcoes", tags=["Rankings & Agregações"])
def listar_gastos_por_funcao(ano: int = Query(2026, description="Ano do exercício")):
    """Retorna a distribuição de despesas por função de governo e percentual do total."""
    return engine.obter_gastos_por_funcao(ano=ano)


@app.get("/api/v1/alertas-corrupcao", tags=["Inteligência & Controle Social"])
def listar_alertas_corrupcao(ano: int = Query(2026, description="Ano do exercício")):
    """
    Retorna despesas sob alerta vermelho de irregularidade grave ou suspeita de corrupção
    (sobrepreço, fracionamento de despesa, fornecedores inidôneos no CEIS/CGU).
    """
    return engine.obter_alertas_corrupcao(ano=ano)


@app.get("/api/v1/fornecedores", tags=["Inteligência & Controle Social"])
def listar_top_fornecedores(
    ano: int = Query(2026, description="Ano do exercício"),
    limite: int = Query(10, ge=1, le=50),
):
    """Retorna os maiores recebedores de recursos públicos, com tipo e quantidade de pagamentos."""
    return engine.obter_top_fornecedores(ano=ano, limite=limite)


@app.get("/api/v1/rastreabilidade/{documento_ou_id}", tags=["Rastreabilidade & Auditoria"])
def obter_rastreabilidade(
    documento_ou_id: str,
):
    """
    Recupera o Contrato de Proveniência completo de um registro ou documento contábil
    (ex: '2026OB800142' ou UUID), fornecendo link direto oficial e hash SHA-256.
    """
    rastro = engine.obter_rastreabilidade(documento_ou_id)
    if not rastro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento ou registro '{documento_ou_id}' não encontrado na base de transparência.",
        )
    return rastro


@app.get("/api/v1/siconfi/municipios", tags=["Estados e Municípios (SICONFI)"])
def listar_dados_municipais(ano: int = Query(2026, description="Ano de exercício")):
    """
    Retorna comparativo fiscal de municípios e estados consolidados via SICONFI,
    incluindo gastos em Saúde, Educação e Gasto por Habitante (per capita) cruzado com o IBGE.
    """
    return extrator_siconfi.obter_amostra_fiscal_municipios(ano=ano)


@app.get("/api/v1/pncp/contratos", tags=["Contratações Públicas (PNCP)"])
def listar_contratos_pncp(ano: int = Query(2026, description="Ano do contrato")):
    """Retorna contratos registrados no Portal Nacional de Contratações Públicas (Lei 14.133/21)."""
    return extrator_pncp.obter_amostra_contratos(ano=ano)


@app.post("/api/v1/pipeline/executar", tags=["Administração"])
def disparar_pipeline(ano: int = Query(2026)):
    """Dispara o pipeline completo de extração, normalização e carga analítica."""
    resumo = executar_pipeline(ano=ano)
    return {
        "status": "sucesso",
        "mensagem": "Pipeline executado com sucesso",
        "resumo": resumo,
    }
