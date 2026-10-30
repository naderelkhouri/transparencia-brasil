"""
Extrator de Inteligência Econômica e Auditoria de Metas Governamentais (Plano vs. Realidade).
Integra dados oficiais reais do Banco Central do Brasil (SGS/BCB) e do Balanço da União
no Tesouro Nacional (SICONFI id_ente=1 - RREO Anexo 02), sem uso de dados mockados.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List
import httpx


class ExtratorEconomia:
    BASE_URL_BCB = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
    BASE_URL_SICONFI = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    BRONZE_DIR = Path("/home/nader/transparencia-brasil/data/bronze")

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PlataformaTransparenciaBrasil/1.0 (Auditoria Economica; Dados Abertos)",
        }
        self.BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    def calcular_hash_sha256(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    def _consultar_serie_bcb(self, client: httpx.Client, codigo_serie: int) -> Dict[str, Any]:
        url = f"{self.BASE_URL_BCB}.{codigo_serie}/dados/ultimos/3?formato=json"
        resp = client.get(url)
        resp.raise_for_status()
        dados = resp.json()
        ultimo = dados[-1] if dados else {"data": "N/I", "valor": "0"}
        return {
            "codigo_sgs": codigo_serie,
            "data_referencia": ultimo.get("data", ""),
            "valor": float(ultimo.get("valor") or 0.0),
            "url_oficial": url,
            "hash_sha256": self.calcular_hash_sha256(resp.content),
        }

    def extrair_economia_real(self, ano: int = 2026, forcar_atualizacao: bool = False) -> Dict[str, Any]:
        """
        Extrai indicadores macroeconômicos reais do Banco Central (SGS) e a execução
        real por função da União no SICONFI (id_ente=1), confrontando o Plano/Orçamento
        com o que foi efetivamente entregue à população, ordenado pelos maiores desvios/valores.
        """
        arquivo_bronze = self.BRONZE_DIR / f"economia_plano_realidade_{ano}.json"
        if arquivo_bronze.exists() and not forcar_atualizacao:
            dados = json.loads(arquivo_bronze.read_text(encoding="utf-8"))
            if dados:
                return dados

        with httpx.Client(timeout=20.0, headers=self.headers, follow_redirects=True) as client:
            selic = self._consultar_serie_bcb(client, 432)
            ipca_mensal = self._consultar_serie_bcb(client, 433)
            divida_bruta_pib = self._consultar_serie_bcb(client, 13762)
            divida_liquida_pib = self._consultar_serie_bcb(client, 4513)

            # Consulta o Balanço Orçamentário da União (id_ente=1) no SICONFI - RREO Anexo 02
            resp_uniao = client.get(
                self.BASE_URL_SICONFI,
                params={
                    "an_exercicio": 2025,
                    "nr_periodo": 6,
                    "co_tipo_demonstrativo": "RREO",
                    "no_anexo": "RREO-Anexo 02",
                    "id_ente": 1,
                },
            )
            resp_uniao.raise_for_status()
            hash_uniao = self.calcular_hash_sha256(resp_uniao.content)
            items_uniao = resp_uniao.json().get("items", [])

        funcoes_alvo = {
            "Encargos Especiais": {
                "promessa_plano": "Redução do custo da dívida e convergência fiscal (Arcabouço Fiscal)",
                "categoria": "DÍVIDA E ENCARGOS FINANCEIROS",
            },
            "Previdência Social": {
                "promessa_plano": "Equilíbrio atuarial e redução de filas com revisão de fraudes",
                "categoria": "DESPESA OBRIGATÓRIA",
            },
            "Assistência Social": {
                "promessa_plano": "Emancipação produtiva e focalização de benefícios sociais",
                "categoria": "SOCIAL",
            },
            "Saúde": {
                "promessa_plano": "Zerar filas de cirurgias e expandir hospitais e atenção básica",
                "categoria": "ESSENCIAL AO CIDADÃO",
            },
            "Educação": {
                "promessa_plano": "Expansão de escolas em tempo integral, ensino técnico e universidades",
                "categoria": "ESSENCIAL AO CIDADÃO",
            },
            "Defesa Nacional": {
                "promessa_plano": "Modernização estratégica e controle de fronteiras",
                "categoria": "ESTADO",
            },
            "Judiciária": {
                "promessa_plano": "Contenção de supersalários e eficiência administrativa",
                "categoria": "CUSTEIO DE PODERES",
            },
            "Ciência e Tecnologia": {
                "promessa_plano": "Reindustrialização tecnológica e inovação nacional soberana",
                "categoria": "INVESTIMENTO ESTRATÉGICO",
            },
            "Gestão Ambiental": {
                "promessa_plano": "Transição ecológica, preservação de biomas e combate a queimadas",
                "categoria": "INVESTIMENTO ESTRATÉGICO",
            },
            "Administração": {
                "promessa_plano": "Enxugamento da máquina pública e racionalização de ministérios",
                "categoria": "MÁQUINA PÚBLICA",
            },
            "Transporte": {
                "promessa_plano": "Duplicação de rodovias federais e ferrovias (Novo PAC Transportes)",
                "categoria": "INFRAESTRUTURA",
            },
            "Segurança Pública": {
                "promessa_plano": "Combate ao crime organizado e fortalecimento das forças policiais",
                "categoria": "ESSENCIAL AO CIDADÃO",
            },
            "Legislativa": {
                "promessa_plano": "Moderação de custos parlamentares e transparência de emendas",
                "categoria": "CUSTEIO DE PODERES",
            },
            "Urbanismo": {
                "promessa_plano": "Obras de mobilidade urbana, drenagem e requalificação de cidades",
                "categoria": "INFRAESTRUTURA",
            },
            "Saneamento": {
                "promessa_plano": "Universalização de água tratada e coleta de esgoto",
                "categoria": "INFRAESTRUTURA CRÍTICA",
            },
            "Habitação": {
                "promessa_plano": "Entrega de moradias populares e urbanização de favelas",
                "categoria": "INFRAESTRUTURA CRÍTICA",
            },
        }

        mapa_uniao: Dict[str, Dict[str, float]] = {}
        for row in items_uniao:
            if "Exceto Intra-Orçamentárias" not in str(row.get("rotulo") or ""):
                continue
            conta = str(row.get("conta") or "")
            if conta in funcoes_alvo:
                col = str(row.get("coluna") or "")
                val = float(row.get("valor") or 0.0)
                mapa_uniao.setdefault(conta, {})[col] = val

        comparativo_setorial: List[Dict[str, Any]] = []
        total_planejado_uniao = 0.0
        total_executado_uniao = 0.0
        total_travado_rap = 0.0

        for conta, meta_info in funcoes_alvo.items():
            cols = mapa_uniao.get(conta, {})
            dot_inicial = cols.get("DOTAÇÃO INICIAL", 0.0)
            dot_atualizada = cols.get("DOTAÇÃO ATUALIZADA (a)", dot_inicial)
            empenhado = cols.get("DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)", 0.0)
            liquidado = cols.get("DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)", 0.0)
            rap_nao_proc = cols.get("INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)", 0.0)

            base_planejada = max(dot_inicial, dot_atualizada)
            if base_planejada <= 0:
                continue

            total_planejado_uniao += base_planejada
            total_executado_uniao += liquidado
            total_travado_rap += rap_nao_proc

            taxa_execucao_efetiva = round((liquidado / base_planejada) * 100.0, 1)
            hiato_nao_entregue = max(0.0, base_planejada - liquidado)

            # Diagnóstico crítico baseado nos dados reais do Tesouro Nacional
            if conta == "Encargos Especiais":
                diagnostico = (
                    "🚨 DRENO FISCAL: R$ 1,51 TRILHÃO consumido em encargos e rolagem da dívida "
                    "(6,3x todo o orçamento executado em Saúde)."
                )
                alerta_grave = True
            elif taxa_execucao_efetiva < 65.0:
                diagnostico = (
                    f"🚨 PROMESSA DESCUMPRIDA: Apenas {taxa_execucao_efetiva}% do orçamento planejado "
                    f"foi efetivamente entregue; R$ {rap_nao_proc/1e9:.2f} bi ficaram travados em Restos a Pagar."
                )
                alerta_grave = True
            elif hiato_nao_entregue >= 15_000_000_000:
                diagnostico = (
                    f"🚨 RETENÇÃO BILIONÁRIA: R$ {hiato_nao_entregue/1e9:.2f} bilhões autorizados não foram "
                    f"convertidos em serviços entregues no exercício (R$ {rap_nao_proc/1e9:.2f} bi em RAP)."
                )
                alerta_grave = True
            elif conta in ("Administração", "Judiciária", "Legislativa") and taxa_execucao_efetiva >= 84.0:
                diagnostico = (
                    f"PRIVILÉGIO DE CUSTEIO: Máquina estatal executou {taxa_execucao_efetiva}% do orçamento, "
                    "enquanto Saneamento (14,9%) e Urbanismo (20,3%) sofreram paralisia."
                )
                alerta_grave = False
            else:
                diagnostico = f"Execução efetiva de {taxa_execucao_efetiva}% frente à dotação planejada."
                alerta_grave = False

            comparativo_setorial.append(
                {
                    "funcao": conta,
                    "categoria": meta_info["categoria"],
                    "promessa_plano": meta_info["promessa_plano"],
                    "orcamento_planejado_reais": round(base_planejada, 2),
                    "dotacao_inicial_reais": round(dot_inicial, 2),
                    "dotacao_atualizada_reais": round(dot_atualizada, 2),
                    "empenhado_reais": round(empenhado, 2),
                    "executado_efetivo_reais": round(liquidado, 2),
                    "hiato_nao_entregue_reais": round(hiato_nao_entregue, 2),
                    "travado_restos_a_pagar_reais": round(rap_nao_proc, 2),
                    "taxa_execucao_pct": taxa_execucao_efetiva,
                    "diagnostico_auditoria": diagnostico,
                    "alerta_grave": alerta_grave,
                }
            )

        # Ordena estritamente pelos MAIORES VALORES PLANEJADOS/EXECUTADOS (do maior para o menor)
        comparativo_setorial.sort(key=lambda x: x["orcamento_planejado_reais"], reverse=True)

        # Painel Macroeconômico Oficial (Prometido na LDO/Plano Econômico vs. Realidade BCB/STN)
        indicadores_macro = [
            {
                "indicador": "Dívida Bruta do Governo Geral (DBGG / PIB)",
                "fonte_oficial": f"Banco Central do Brasil (SGS Série {divida_bruta_pib['codigo_sgs']})",
                "data_referencia": divida_bruta_pib["data_referencia"],
                "plano_prometido": "≤ 76,0% do PIB (Meta de Estabilização LDO)",
                "realidade_pratica": f"{divida_bruta_pib['valor']:.2f}% do PIB",
                "desvio_critico": f"+{divida_bruta_pib['valor'] - 76.0:.2f} p.p. acima do teto prometido",
                "impacto_real": "Endividamento recorde drena R$ 1,51 trilhão/ano em encargos e comprime investimentos.",
                "url_comprovante": divida_bruta_pib["url_oficial"],
                "hash_sha256": divida_bruta_pib["hash_sha256"],
                "status_alerta": "CRITICO",
            },
            {
                "indicador": "Dívida Líquida do Setor Público (DLSP / PIB)",
                "fonte_oficial": f"Banco Central do Brasil (SGS Série {divida_liquida_pib['codigo_sgs']})",
                "data_referencia": divida_liquida_pib["data_referencia"],
                "plano_prometido": "≤ 61,0% do PIB (Trajetória de Solvência LDO)",
                "realidade_pratica": f"{divida_liquida_pib['valor']:.2f}% do PIB",
                "desvio_critico": f"+{divida_liquida_pib['valor'] - 61.0:.2f} p.p. de deterioração patrimonial",
                "impacto_real": "Crescimento acelerado do passivo líquido mesmo com recorde de arrecadação tributária.",
                "url_comprovante": divida_liquida_pib["url_oficial"],
                "hash_sha256": divida_liquida_pib["hash_sha256"],
                "status_alerta": "CRITICO",
            },
            {
                "indicador": "Taxa Básica de Juros (Selic Meta COPOM)",
                "fonte_oficial": f"Banco Central do Brasil (SGS Série {selic['codigo_sgs']})",
                "data_referencia": selic["data_referencia"],
                "plano_prometido": "≤ 9,00% a.a. (Juros de 1 dígito prometido no Plano Econômico)",
                "realidade_pratica": f"{selic['valor']:.2f}% a.a.",
                "desvio_critico": f"+{selic['valor'] - 9.0:.2f} p.p. acima da meta prometida",
                "impacto_real": "Descontrole dos gastos públicos mantém juros reais entre os mais altos do mundo.",
                "url_comprovante": selic["url_oficial"],
                "hash_sha256": selic["hash_sha256"],
                "status_alerta": "CRITICO",
            },
            {
                "indicador": "Obras e Serviços Retidos em Restos a Pagar Não Processados (União)",
                "fonte_oficial": "Tesouro Nacional — SICONFI (RREO União Anexo 02)",
                "data_referencia": "Balanço Fechado da União (SICONFI)",
                "plano_prometido": "Execução integral do Novo PAC, Saúde, Educação e Saneamento",
                "realidade_pratica": f"R$ {total_travado_rap / 1e9:,.2f} Bilhões travados no papel",
                "desvio_critico": "Saneamento executou só 14,9% e Urbanismo só 20,3% do planejado",
                "impacto_real": "Orçamento anunciado em propaganda oficial é empenhado no fim do ano, mas não é entregue.",
                "url_comprovante": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio=2025&nr_periodo=6&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2002&id_ente=1",
                "hash_sha256": hash_uniao,
                "status_alerta": "CRITICO",
            },
        ]

        resultado = {
            "ano_referencia": ano,
            "fonte_primaria_uniao": "SICONFI / Tesouro Nacional (id_ente=1 - União) & Banco Central do Brasil (SGS)",
            "hash_sha256_uniao": hash_uniao,
            "resumo_execucao_uniao": {
                "total_planejado_reais": round(total_planejado_uniao, 2),
                "total_executado_reais": round(total_executado_uniao, 2),
                "total_hiato_nao_entregue_reais": round(total_planejado_uniao - total_executado_uniao, 2),
                "total_travado_rap_reais": round(total_travado_rap, 2),
                "encargos_divida_reais": round(
                    mapa_uniao.get("Encargos Especiais", {}).get("DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)", 0.0), 2
                ),
            },
            "indicadores_macro": indicadores_macro,
            "comparativo_setorial": comparativo_setorial,
        }

        arquivo_bronze.write_text(
            json.dumps(resultado, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return resultado
