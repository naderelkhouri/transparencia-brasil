# 🏛️ Transparência Brasil — Plataforma de Gastos Públicos Confiáveis

> 🌐 **Acesso Online ao Vivo:** [https://beverages-slowly-gabriel-laboratory.trycloudflare.com](https://beverages-slowly-gabriel-laboratory.trycloudflare.com)  
> 📚 **Documentação da API Swagger:** [https://beverages-slowly-gabriel-laboratory.trycloudflare.com/docs](https://beverages-slowly-gabriel-laboratory.trycloudflare.com/docs)  
> 🚨 **Radar Anti-Corrupção:** [https://beverages-slowly-gabriel-laboratory.trycloudflare.com/#radar](https://beverages-slowly-gabriel-laboratory.trycloudflare.com/)

Plataforma aberta para consolidação, conciliação e rastreabilidade dos gastos públicos brasileiros (União, Estados e Municípios), desenvolvida em estrita conformidade com as normas financeiras brasileiras:
- **Lei nº 4.320/1964** (Estatuto das Finanças Públicas e Ciclo Orçamentário)
- **Lei Complementar nº 101/2000** (Lei de Responsabilidade Fiscal - LRF)
- **Lei nº 12.527/2011** (Lei de Acesso à Informação - LAI)
- **Lei nº 14.133/2021** (Nova Lei de Licitações e Contratos Administrativos)

---

## 🌟 Diferenciais e Rigor Técnico

1. **Prevenção da Dupla Contagem (Anti-Bitributação de Repasses):**
   - Repasses fundo a fundo da União para Estados e Municípios (ex: Fundo Nacional de Saúde repassando ao Fundo Municipal de Saúde) são isolados e etiquetados com a flag `is_transferencia_intergovernamental`. O total de **Gasto Efetivo Nacional** deduz repasses intermediários para evitar inflar o montante em duas esferas.
2. **Ciclo Orçamentário Completo vs. Gasto Efetivo:**
   - A métrica padrão do cidadão é o **Valor Pago Líquido**. No modo Auditoria/Controle Social, é exibido o funil contábil formal:
   ```
   Dotação Autorizada ➔ Empenho Líquido (NE) ➔ Liquidação Atestada (NL) ➔ Pagamento Efetivo (OB)
   ```
3. **Rastreabilidade e Proveniência Forense (1-Click):**
   - Todo registro exibe o número oficial da Ordem Bancária ou Nota de Empenho, o hash SHA-256 do arquivo original e o link oficial direto para consulta no Portal da Transparência da CGU, SICONFI ou PNCP.

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FONTES GOVERNAMENTAIS OFICIAIS                       │
│     CGU / SIAFI      │    Tesouro / SICONFI    │    PNCP / Compras.gov      │
└─────────────┬────────┴──────────────┬──────────┴──────────────┬─────────────┘
              ▼                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA BRONZE (RAW STORAGE)                       │
│    CSVs brutos, JSONs e payloads originais com assinatura SHA-256           │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CAMADA SILVER (DUCKDB + PARQUET)                        │
│    • Deduplicação contábil idempotente                                      │
│    • Dedução de anulações de empenho e estornos                             │
│    • Isolamento de transferências intergovernamentais                      │
│    • Armazenamento particionado em Parquet: /data/silver/ano={ano}/...      │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CAMADA GOLD (BANCO ANALÍTICO OLAP)                      │
│    • DuckDB in-process de alta performance (e/ou ClickHouse em produção)   │
│    • Agregações materializadas e funil orçamentário em milissegundos        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     API REST (FASTAPI) & WEB DASHBOARD                      │
│    • Endpoints OpenAPI 3.1 com busca em tempo real e paginação              │
│    • Interface SPA responsiva (Visão Cidadã vs. Modo Auditor)               │
│    • Modal de Rastreabilidade com link para o documento original            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Como Executar Localmente

### Pré-requisitos
- Python 3.12+ (gerenciado automaticamente pelo script via `uv`)
- `uv` instalado

### 1. Inicialização Rápida (1 Comando)
Execute o script inicializador na raiz do projeto:
```bash
./start.sh
```

O script irá:
1. Criar o ambiente virtual e instalar as dependências via `uv`.
2. Executar o pipeline de ingestão (Bronze ➔ Silver ➔ Gold).
3. Iniciar o servidor HTTP em `http://localhost:8000`.

### 2. Acessos
- 🌐 **Painel Web Interativo:** [http://localhost:8000](http://localhost:8000)
- 📚 **Documentação da API (Swagger / OpenAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- 📖 **Documentação Alternativa (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testes Automatizados

O projeto conta com suite completa de testes contábeis e de integração:
```bash
.venv/bin/pytest -v
```

Cobertura dos testes:
- Cálculo do valor líquido deduzindo anulações contábeis.
- Prevenção de dupla contagem em repasses intergovernamentais.
- Deduplicação idempotente na camada Silver.
- Integridade da proveniência com hash SHA-256 e URLs oficiais.
- Endpoints da API REST (Health, Resumo, Órgãos, Fornecedores, Municípios, PNCP, Rastreabilidade).

---

## 📁 Estrutura de Diretórios

```
transparencia-brasil/
├── apps/
│   ├── api/
│   │   └── main.py                     # API FastAPI e rotas REST
│   └── web/
│       └── static/                     # Frontend SPA interativo
│           ├── index.html              # Interface do cidadão e auditor
│           ├── css/app.css             # Estilos modernos e responsivos
│           └── js/app.js               # Lógica de consumo da API e modal
├── packages/
│   └── pipeline/
│       ├── models.py                   # Modelos de dados e enums (Lei 4.320/64)
│       ├── normalizer.py               # Camada Silver (Parquet e deduplicação)
│       ├── gold_engine.py              # Camada Gold (DuckDB / ClickHouse)
│       ├── run_pipeline.py             # Script de orquestração do pipeline
│       ├── extractors/
│       │   ├── cgu_extractor.py        # Portal da Transparência / CGU
│       │   ├── siconfi_extractor.py    # Tesouro Nacional / SICONFI
│       │   └── pncp_extractor.py       # Contratações Públicas / PNCP
│       └── tests/
│           ├── test_pipeline.py        # Testes contábeis e de integridade
│           └── test_api.py             # Testes dos endpoints HTTP
├── data/
│   ├── bronze/                         # Arquivos brutos e payloads originais
│   ├── silver/                         # Arquivos Parquet particionados
│   └── gold/                           # Banco analítico DuckDB
├── infra/
│   ├── Dockerfile                      # Imagem de produção da API
│   └── docker-compose.yml              # ClickHouse, PostgreSQL, MinIO e Redis
├── pyproject.toml                      # Metadados do projeto Python
├── start.sh                            # Script executável de inicialização
└── README.md                           # Documentação técnica
```
