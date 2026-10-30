"""
Gera o Cloudflare Edge Worker (infra/cloudflare-worker.js) com os dados reais
sincronizados na camada Gold/Bronze e ativos estáticos otimizados para *.admx.tech.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from apps.api.main import app


def main():
    client = TestClient(app)

    index_html = Path("apps/web/static/index.html").read_text(encoding="utf-8")
    app_css = Path("apps/web/static/css/app.css").read_text(encoding="utf-8")
    app_js = Path("apps/web/static/js/app.js").read_text(encoding="utf-8")

    resumo = client.get("/api/v1/resumo?ano=2026").json()
    alertas = client.get("/api/v1/alertas-corrupcao?ano=2026").json()
    orgaos = client.get("/api/v1/orgaos?ano=2026&limite=15").json()
    funcoes = client.get("/api/v1/funcoes?ano=2026").json()
    fornecedores = client.get("/api/v1/fornecedores?ano=2026&limite=20").json()
    despesas_full = client.get("/api/v1/despesas?ano=2026&limite=200").json()
    municipios = client.get("/api/v1/siconfi/municipios?ano=2026").json()
    contratos = client.get("/api/v1/pncp/contratos?ano=2026").json()
    csv_all = client.get("/api/v1/exportar/despesas.csv?ano=2026&apenas_corrupcao=false").text
    csv_corr = client.get("/api/v1/exportar/despesas.csv?ano=2026&apenas_corrupcao=true").text
    sitemap_xml = client.get("/sitemap.xml").text
    robots_txt = client.get("/robots.txt").text

    rastreabilidade_map = {}
    for item in despesas_full["itens"]:
        doc = item["numero_documento"]
        r = client.get(f"/api/v1/rastreabilidade/{doc}")
        if r.status_code == 200:
            rastreabilidade_map[doc] = r.json()
            rastreabilidade_map[item["id"]] = r.json()

    worker_code = f"""// Cloudflare Edge Worker - Transparência Brasil (*.admx.tech)
const INDEX_HTML = {json.dumps(index_html, ensure_ascii=False)};
const APP_CSS = {json.dumps(app_css, ensure_ascii=False)};
const APP_JS = {json.dumps(app_js, ensure_ascii=False)};
const ROBOTS_TXT = {json.dumps(robots_txt, ensure_ascii=False)};
const SITEMAP_XML = {json.dumps(sitemap_xml, ensure_ascii=False)};
const DATA_RESUMO = {json.dumps(resumo, ensure_ascii=False)};
const DATA_ALERTAS = {json.dumps(alertas, ensure_ascii=False)};
const DATA_ORGAOS = {json.dumps(orgaos, ensure_ascii=False)};
const DATA_FUNCOES = {json.dumps(funcoes, ensure_ascii=False)};
const DATA_FORNECEDORES = {json.dumps(fornecedores, ensure_ascii=False)};
const DATA_DESPESAS = {json.dumps(despesas_full["itens"], ensure_ascii=False)};
const DATA_MUNICIPIOS = {json.dumps(municipios, ensure_ascii=False)};
const DATA_CONTRATOS = {json.dumps(contratos, ensure_ascii=False)};
const DATA_RASTRO = {json.dumps(rastreabilidade_map, ensure_ascii=False)};
const CSV_ALL = {json.dumps(csv_all, ensure_ascii=False)};
const CSV_CORR = {json.dumps(csv_corr, ensure_ascii=False)};

const SEC_HEADERS = {{
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "SAMEORIGIN",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Access-Control-Allow-Origin": "*"
}};

function jsonResp(obj, status = 200) {{
  return new Response(JSON.stringify(obj), {{
    status,
    headers: {{ ...SEC_HEADERS, "Content-Type": "application/json; charset=utf-8" }}
  }});
}}

export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === "/" || path === "/index.html") {{
      return new Response(INDEX_HTML, {{
        status: 200,
        headers: {{ ...SEC_HEADERS, "Content-Type": "text/html; charset=utf-8" }}
      }});
    }}
    if (path === "/static/css/app.css") {{
      return new Response(APP_CSS, {{
        status: 200,
        headers: {{ ...SEC_HEADERS, "Content-Type": "text/css; charset=utf-8" }}
      }});
    }}
    if (path === "/static/js/app.js") {{
      return new Response(APP_JS, {{
        status: 200,
        headers: {{ ...SEC_HEADERS, "Content-Type": "application/javascript; charset=utf-8" }}
      }});
    }}
    if (path === "/robots.txt") {{
      return new Response(ROBOTS_TXT, {{
        status: 200,
        headers: {{ ...SEC_HEADERS, "Content-Type": "text/plain; charset=utf-8" }}
      }});
    }}
    if (path === "/sitemap.xml") {{
      return new Response(SITEMAP_XML, {{
        status: 200,
        headers: {{ ...SEC_HEADERS, "Content-Type": "application/xml; charset=utf-8" }}
      }});
    }}
    if (path === "/health") {{
      return jsonResp({{ status: "online", banco_analitico: "conectado", registros_carregados: DATA_DESPESAS.length }});
    }}
    if (path === "/api/v1/resumo") {{
      return jsonResp(DATA_RESUMO);
    }}
    if (path === "/api/v1/alertas-corrupcao") {{
      return jsonResp(DATA_ALERTAS);
    }}
    if (path === "/api/v1/orgaos") {{
      return jsonResp(DATA_ORGAOS);
    }}
    if (path === "/api/v1/funcoes") {{
      return jsonResp(DATA_FUNCOES);
    }}
    if (path === "/api/v1/fornecedores") {{
      return jsonResp(DATA_FORNECEDORES);
    }}
    if (path === "/api/v1/siconfi/municipios") {{
      return jsonResp(DATA_MUNICIPIOS);
    }}
    if (path === "/api/v1/pncp/contratos") {{
      return jsonResp(DATA_CONTRATOS);
    }}
    if (path === "/api/v1/despesas") {{
      const busca = (url.searchParams.get("busca") || "").toLowerCase();
      const apenasCorr = url.searchParams.get("apenas_corrupcao") === "true";
      const orgao = url.searchParams.get("orgao") || "";
      let itens = DATA_DESPESAS;
      if (orgao) itens = itens.filter(d => d.orgao === orgao);
      if (apenasCorr) itens = itens.filter(d => d.alerta_corrupcao === true);
      if (busca) {{
        itens = itens.filter(d =>
          (d.favorecido_nome || "").toLowerCase().includes(busca) ||
          (d.numero_documento || "").toLowerCase().includes(busca) ||
          (d.acao || "").toLowerCase().includes(busca)
        );
      }}
      return jsonResp({{ total_encontrado: itens.length, limite: 50, offset: 0, itens: itens.slice(0, 50) }});
    }}
    if (path.startsWith("/api/v1/rastreabilidade/")) {{
      const docId = decodeURIComponent(path.replace("/api/v1/rastreabilidade/", ""));
      const item = DATA_RASTRO[docId];
      if (!item) return jsonResp({{ detail: "Documento não encontrado" }}, 404);
      return jsonResp(item);
    }}
    if (path === "/api/v1/exportar/despesas.csv") {{
      const apenasCorr = url.searchParams.get("apenas_corrupcao") === "true";
      const body = apenasCorr ? CSV_CORR : CSV_ALL;
      const fname = apenasCorr ? "dossie_alertas_corrupcao_2026.csv" : "despesas_publicas_2026.csv";
      return new Response(body, {{
        status: 200,
        headers: {{
          ...SEC_HEADERS,
          "Content-Type": "text/csv; charset=utf-8",
          "Content-Disposition": "attachment; filename=" + fname
        }}
      }});
    }}
    return jsonResp({{ detail: "Not Found" }}, 404);
  }}
}};
"""

    out_path = Path("infra/cloudflare-worker.js")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(worker_code, encoding="utf-8")
    print(f"Worker generated successfully at {out_path} ({len(worker_code)} bytes)")


if __name__ == "__main__":
    main()
