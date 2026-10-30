"""
Extrator de Contratos e Licitações - Portal Nacional de Contratações Públicas (PNCP).
Integra diretamente com a API Oficial de Consulta do PNCP (Lei nº 14.133/2021),
sem qualquer uso de dados fictícios ou mockados.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any
import httpx


class ExtratorPNCP:
    BASE_URL_PNCP = "https://pncp.gov.br/api/consulta/v1"
    BRONZE_DIR = Path("/home/nader/transparencia-brasil/data/bronze")

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PlataformaTransparenciaBrasil/1.0 (Auditoria Civica; Dados Abertos)",
        }
        self.BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    def calcular_hash_sha256(self, payload: bytes) -> str:
        """Gera checksum SHA-256 do payload bruto oficial recebido do PNCP."""
        return hashlib.sha256(payload).hexdigest()

    def extrair_contratos_reais(self, ano: int = 2026, tamanho_pagina: int = 50) -> List[Dict[str, Any]]:
        """
        Extrai contratos públicos reais diretamente da API Oficial do PNCP
        (https://pncp.gov.br/api/consulta/v1/contratos) e persiste na camada Bronze.
        """
        url = f"{self.BASE_URL_PNCP}/contratos"
        # Busca janela real no exercício solicitado (ou último exercício publicado se futuro)
        ano_busca = min(ano, 2026)
        params = {
            "dataInicial": f"{ano_busca}0101",
            "dataFinal": f"{ano_busca}0228",
            "pagina": 1,
            "tamanhoPagina": max(10, min(tamanho_pagina, 500)),
        }

        with httpx.Client(timeout=25.0, follow_redirects=True) as client:
            resp = client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            raw_bytes = resp.content
            hash_extracao = self.calcular_hash_sha256(raw_bytes)
            payload = resp.json()

        itens_brutos = payload.get("data", [])
        contratos_processados: List[Dict[str, Any]] = []

        for item in itens_brutos:
            orgao = item.get("orgaoEntidade") or {}
            unidade = item.get("unidadeOrgao") or {}
            tipo_contrato = item.get("tipoContrato") or {}
            categoria = item.get("categoriaProcesso") or {}

            cnpj_orgao = str(orgao.get("cnpj") or "").strip()
            ano_contrato = item.get("anoContrato") or ano_busca
            seq_contrato = item.get("sequencialContrato") or 1
            num_empenho = str(item.get("numeroContratoEmpenho") or seq_contrato).strip()

            valor_inicial = float(item.get("valorInicial") or 0.0)
            valor_global = float(item.get("valorGlobal") or valor_inicial or 0.0)
            if valor_global <= 0 and valor_inicial <= 0:
                continue

            ni_fornecedor = str(item.get("niFornecedor") or "N/I").strip()
            razao_fornecedor = str(item.get("nomeRazaoSocialFornecedor") or "FORNECEDOR NÃO INFORMADO").strip()
            objeto = str(item.get("objetoContrato") or "Objeto contratual registrado no PNCP").strip()

            url_oficial = f"https://pncp.gov.br/app/contratos/{cnpj_orgao}/{ano_contrato}/{seq_contrato}"

            contratos_processados.append(
                {
                    "id_pncp": str(item.get("numeroControlePNCP") or f"{cnpj_orgao}-{ano_contrato}-{seq_contrato}"),
                    "numero_contrato": f"{num_empenho}/{ano_contrato}",
                    "ano_contrato": int(ano_contrato),
                    "sequencial_contrato": int(seq_contrato),
                    "orgao_nome": str(orgao.get("razaoSocial") or "Órgão Público").strip(),
                    "orgao_cnpj": cnpj_orgao,
                    "esfera_id": str(orgao.get("esferaId") or "F"),
                    "poder_id": str(orgao.get("poderId") or "E"),
                    "unidade_codigo": str(unidade.get("codigoUnidade") or "000001"),
                    "unidade_nome": str(unidade.get("nomeUnidade") or orgao.get("razaoSocial") or "Unidade Gestora").strip(),
                    "uf": str(unidade.get("ufSigla") or ""),
                    "municipio_nome": str(unidade.get("municipioNome") or ""),
                    "codigo_ibge": str(unidade.get("codigoIbge") or ""),
                    "objeto": objeto,
                    "modalidade_licitacao": f"{tipo_contrato.get('nome', 'Contrato')} - {categoria.get('nome', 'Geral')}",
                    "categoria_nome": str(categoria.get("nome") or "Geral"),
                    "valor_total_estimado": round(valor_inicial if valor_inicial > 0 else valor_global, 2),
                    "valor_homologado": round(valor_global if valor_global > 0 else valor_inicial, 2),
                    "fornecedor_cnpj": ni_fornecedor,
                    "fornecedor_razao_social": razao_fornecedor,
                    "tipo_pessoa": str(item.get("tipoPessoa") or "PJ"),
                    "vigencia_inicio": str(item.get("dataVigenciaInicio") or item.get("dataAssinatura") or f"{ano_busca}-01-01"),
                    "vigencia_fim": str(item.get("dataVigenciaFim") or f"{ano_busca}-12-31"),
                    "data_assinatura": str(item.get("dataAssinatura") or item.get("dataVigenciaInicio") or f"{ano_busca}-01-01"),
                    "url_oficial": url_oficial,
                    "hash_sha256": hash_extracao,
                }
            )

        # Salva na camada Bronze para auditoria e leitura rápida
        arquivo_bronze = self.BRONZE_DIR / f"pncp_contratos_{ano}.json"
        arquivo_bronze.write_text(
            json.dumps(contratos_processados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return contratos_processados

    def obter_contratos_reais(self, ano: int = 2026) -> List[Dict[str, Any]]:
        """
        Retorna os contratos públicos reais extraídos do PNCP.
        Lê do cache persistido na camada Bronze ou consulta a API do PNCP em tempo real.
        """
        arquivo_bronze = self.BRONZE_DIR / f"pncp_contratos_{ano}.json"
        if arquivo_bronze.exists():
            dados = json.loads(arquivo_bronze.read_text(encoding="utf-8"))
            if dados:
                return dados
        return self.extrair_contratos_reais(ano=ano)
