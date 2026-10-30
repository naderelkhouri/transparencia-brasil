"""
Extrator de Dados Fiscais Subnacionais - SICONFI / Secretaria do Tesouro Nacional (STN).
Integra diretamente com a API Datalake do Tesouro Nacional (RREO Anexo 01 e Anexo 02),
sem uso de dados mockados ou fictícios.
"""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Any
import httpx


class ExtratorSiconfi:
    BASE_URL_DATALAKE = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
    BRONZE_DIR = Path("/home/nader/transparencia-brasil/data/bronze")

    CAPITAIS_MONITORADAS = [
        (3550308, "São Paulo", "SP"),
        (3304557, "Rio de Janeiro", "RJ"),
        (3106200, "Belo Horizonte", "MG"),
        (2927408, "Salvador", "BA"),
        (4106902, "Curitiba", "PR"),
        (4314902, "Porto Alegre", "RS"),
    ]

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PlataformaTransparenciaBrasil/1.0 (Auditoria Civica; Dados Abertos)",
        }
        self.BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    def calcular_hash_sha256(self, payload: bytes) -> str:
        """Gera checksum SHA-256 do payload bruto oficial recebido do SICONFI/STN."""
        return hashlib.sha256(payload).hexdigest()

    def _extrair_capital_siconfi(self, args: tuple) -> Dict[str, Any]:
        cod_ibge, nome_municipio, uf, ano = args
        # Consulta o exercício solicitado; se o 6º bimestre do exercício em curso ainda não foi
        # homologado no SICONFI, utiliza o último RREO anual fechado homologado pelo Tesouro (2025/6º bim).
        exercicios_tentativa = [(ano, 1), (2025, 6), (2024, 6)]
        items_a1: List[Dict[str, Any]] = []
        items_a2: List[Dict[str, Any]] = []
        hash_a1 = ""
        exercicio_efetivo = 2025
        periodo_efetivo = 6

        with httpx.Client(timeout=20.0, headers=self.headers) as client:
            for ex, per in exercicios_tentativa:
                r1 = client.get(
                    f"{self.BASE_URL_DATALAKE}/rreo",
                    params={
                        "an_exercicio": ex,
                        "nr_periodo": per,
                        "co_tipo_demonstrativo": "RREO",
                        "no_anexo": "RREO-Anexo 01",
                        "id_ente": cod_ibge,
                    },
                )
                if r1.status_code == 200:
                    dados1 = r1.json().get("items", [])
                    if dados1:
                        items_a1 = dados1
                        hash_a1 = self.calcular_hash_sha256(r1.content)
                        exercicio_efetivo = ex
                        periodo_efetivo = per
                        break

            r2 = client.get(
                f"{self.BASE_URL_DATALAKE}/rreo",
                params={
                    "an_exercicio": exercicio_efetivo,
                    "nr_periodo": periodo_efetivo,
                    "co_tipo_demonstrativo": "RREO",
                    "no_anexo": "RREO-Anexo 02",
                    "id_ente": cod_ibge,
                },
            )
            if r2.status_code == 200:
                items_a2 = r2.json().get("items", [])

        populacao_ibge = int(items_a1[0].get("populacao") or 1) if items_a1 else 1
        dotacao_atualizada = 0.0
        despesa_empenhada = 0.0
        despesa_liquidada = 0.0
        despesa_paga = 0.0
        restos_a_pagar = 0.0

        for row in items_a1:
            if row.get("cod_conta") == "DespesasExcetoIntraOrcamentarias":
                col = str(row.get("coluna") or "").upper()
                val = float(row.get("valor") or 0.0)
                if "DOTAÇÃO ATUALIZADA" in col:
                    dotacao_atualizada = val
                elif "DESPESAS EMPENHADAS ATÉ O BIMESTRE" in col:
                    despesa_empenhada = val
                elif "DESPESAS LIQUIDADAS ATÉ O BIMESTRE" in col:
                    despesa_liquidada = val
                elif "DESPESAS PAGAS ATÉ O BIMESTRE" in col:
                    despesa_paga = val
                elif "RESTOS A PAGAR" in col:
                    restos_a_pagar = val

        gasto_saude = 0.0
        gasto_educacao = 0.0
        for row in items_a2:
            rotulo = str(row.get("rotulo") or "")
            col = str(row.get("coluna") or "").upper()
            conta = str(row.get("conta") or "")
            if "Exceto Intra-Orçamentárias" in rotulo and "DESPESAS LIQUIDADAS ATÉ O BIMESTRE" in col:
                if conta == "Saúde":
                    gasto_saude = float(row.get("valor") or 0.0)
                elif conta == "Educação":
                    gasto_educacao = float(row.get("valor") or 0.0)

        base_calculo_paga = despesa_paga if despesa_paga > 0 else despesa_liquidada
        gasto_per_capita = round(base_calculo_paga / max(1, populacao_ibge), 2)

        return {
            "codigo_ibge": cod_ibge,
            "municipio": nome_municipio,
            "uf": uf,
            "exercicio_rreo": exercicio_efetivo,
            "bimestre_rreo": periodo_efetivo,
            "populacao_ibge": populacao_ibge,
            "orcamento_aprovado": round(dotacao_atualizada, 2),
            "despesa_empenhada": round(despesa_empenhada, 2),
            "despesa_liquidada": round(despesa_liquidada, 2),
            "despesa_paga": round(base_calculo_paga, 2),
            "restos_a_pagar": round(restos_a_pagar, 2),
            "gasto_saude": round(gasto_saude, 2),
            "gasto_educacao": round(gasto_educacao, 2),
            "gasto_per_capita": gasto_per_capita,
            "hash_sha256": hash_a1,
            "fonte_url": f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={exercicio_efetivo}&nr_periodo={periodo_efetivo}&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2001&id_ente={cod_ibge}",
        }

    def extrair_dados_municipios_reais(self, ano: int = 2026) -> List[Dict[str, Any]]:
        """
        Consulta em paralelo os demonstrativos RREO Anexo 01 e Anexo 02 na API oficial
        do SICONFI/Tesouro Nacional para as capitais brasileiras e salva na camada Bronze.
        """
        tarefas = [(cod, nome, uf, ano) for (cod, nome, uf) in self.CAPITAIS_MONITORADAS]
        with ThreadPoolExecutor(max_workers=6) as executor:
            resultados = list(executor.map(self._extrair_capital_siconfi, tarefas))

        resultados = [r for r in resultados if r["despesa_paga"] > 0]
        resultados.sort(key=lambda x: x["despesa_paga"], reverse=True)

        arquivo_bronze = self.BRONZE_DIR / f"siconfi_municipios_{ano}.json"
        arquivo_bronze.write_text(
            json.dumps(resultados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return resultados

    def obter_dados_municipios_reais(self, ano: int = 2026) -> List[Dict[str, Any]]:
        """
        Retorna os dados fiscais reais de municípios extraídos da API SICONFI/STN.
        """
        arquivo_bronze = self.BRONZE_DIR / f"siconfi_municipios_{ano}.json"
        if arquivo_bronze.exists():
            dados = json.loads(arquivo_bronze.read_text(encoding="utf-8"))
            if dados:
                return dados
        return self.extrair_dados_municipios_reais(ano=ano)
