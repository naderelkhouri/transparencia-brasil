"""
Normalizador da Camada Silver:
- Validação de integridade contábil
- Deduplicação idempotente
- Prevenção de bitributação em transferências
- Exportação em arquivos Parquet particionados
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import pyarrow as pa
import pyarrow.parquet as pq
from .models import RegistroDespesaCanonica


class NormalizadorSilver:
    def __init__(self, output_dir: str = "/home/nader/transparencia-brasil/data/silver"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def deduplicar_e_validar(self, registros: List[RegistroDespesaCanonica]) -> List[RegistroDespesaCanonica]:
        """
        Deduplica registros baseado na chave única natural contábil:
        (ente_federativo, numero_documento_origem, tipo_documento, data_evento, fase_despesa)
        """
        registros_unicos: Dict[str, RegistroDespesaCanonica] = {}

        for reg in registros:
            # Chave natural do evento contábil
            chave = f"{reg.ente_federativo}:{reg.numero_documento_origem}:{reg.tipo_documento}:{reg.data_evento}:{reg.fase_despesa.value}"

            if chave in registros_unicos:
                # Mantém a versão mais recente caso haja reprocessamento
                if reg.versao_registro >= registros_unicos[chave].versao_registro:
                    registros_unicos[chave] = reg
            else:
                registros_unicos[chave] = reg

        return list(registros_unicos.values())

    def salvar_parquet(self, registros: List[RegistroDespesaCanonica]) -> List[str]:
        """
        Salva os registros validados em formato Parquet particionado por ano e esfera.
        Retorna lista de caminhos dos arquivos Parquet gerados.
        """
        registros_limpos = self.deduplicar_e_validar(registros)
        if not registros_limpos:
            return []

        # Agrupar por (ano_exercicio, esfera)
        grupos: Dict[tuple, List[Dict[str, Any]]] = {}
        for reg in registros_limpos:
            chave_particao = (reg.ano_exercicio, reg.esfera.value)
            if chave_particao not in grupos:
                grupos[chave_particao] = []

            grupos[chave_particao].append({
                "id": reg.id,
                "ente_federativo": reg.ente_federativo,
                "esfera": reg.esfera.value,
                "poder": reg.poder.value,
                "codigo_orgao_superior": reg.codigo_orgao_superior,
                "nome_orgao_superior": reg.nome_orgao_superior,
                "codigo_unidade_gestora": reg.codigo_unidade_gestora,
                "nome_unidade_gestora": reg.nome_unidade_gestora,
                "ano_exercicio": reg.ano_exercicio,
                "data_evento": str(reg.data_evento),
                "data_competencia": str(reg.data_competencia),
                "funcao_governo": reg.funcao_governo,
                "subfuncao_governo": reg.subfuncao_governo,
                "programa_governo": reg.programa_governo,
                "acao_governamental": reg.acao_governamental,
                "elemento_despesa": reg.elemento_despesa,
                "fase_despesa": reg.fase_despesa.value,
                "valor_bruto_centavos": reg.valor_bruto_centavos,
                "valor_anulacoes_centavos": reg.valor_anulacoes_centavos,
                "valor_liquido_centavos": reg.valor_liquido_centavos,
                "valor_liquido_reais": reg.valor_liquido_reais,
                "is_transferencia_intergovernamental": reg.is_transferencia_intergovernamental,
                "ente_destinatario": reg.ente_destinatario or "",
                "tipo_documento": reg.tipo_documento,
                "numero_documento_origem": reg.numero_documento_origem,
                "codigo_processo_licitatorio": reg.codigo_processo_licitatorio or "",
                "id_contrato_pncp": reg.id_contrato_pncp or "",
                "favorecido_tipo": reg.favorecido_tipo.value,
                "favorecido_documento": reg.favorecido_documento,
                "favorecido_nome": reg.favorecido_nome,
                "fonte_identificador": reg.fonte_identificador,
                "url_comprovante_oficial": reg.url_comprovante_oficial,
                "hash_payload_extracao": reg.hash_payload_extracao,
                "data_ingestao": reg.data_ingestao.isoformat(),
                "versao_registro": reg.versao_registro,
                "alerta_corrupcao": reg.alerta_corrupcao,
                "motivo_alerta_corrupcao": reg.motivo_alerta_corrupcao or "",
                "tipo_risco_corrupcao": reg.tipo_risco_corrupcao or "",
            })

        arquivos_gerados = []
        for (ano, esfera), linhas in grupos.items():
            pasta_particao = self.output_dir / f"ano={ano}" / f"esfera={esfera}"
            pasta_particao.mkdir(parents=True, exist_ok=True)
            caminho_arquivo = pasta_particao / "despesas.parquet"

            tabela = pa.Table.from_pylist(linhas)
            pq.write_table(tabela, caminho_arquivo, compression="zstd")
            arquivos_gerados.append(str(caminho_arquivo))

        return arquivos_gerados
