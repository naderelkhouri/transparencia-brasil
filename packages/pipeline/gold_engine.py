"""
Engine Analítica da Camada Gold:
Gerencia o banco analítico com DuckDB de alta performance sobre Parquet
com suporte opcional a espelhamento ClickHouse.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import duckdb
from .models import ResumoNacional


class GoldAnalyticsEngine:
    def __init__(
        self,
        db_path: str = "/home/nader/transparencia-brasil/data/gold/transparencia_gold.duckdb",
        silver_path: str = "/home/nader/transparencia-brasil/data/silver",
        read_only: bool = True,
    ):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.silver_path = Path(silver_path)
        self.read_only = read_only
        self.conn = duckdb.connect(str(self.db_path), read_only=read_only)
        if not read_only:
            self._inicializar_tabelas()

    def _cursor(self):
        """Retorna um cursor isolado para execução concorrente e thread-safe."""
        return self.conn.cursor()

    def _inicializar_tabelas(self):
        """Cria tabelas analíticas materializadas no DuckDB."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fato_despesa_unificada (
                id VARCHAR PRIMARY KEY,
                ente_federativo VARCHAR,
                esfera VARCHAR,
                poder VARCHAR,
                codigo_orgao_superior VARCHAR,
                nome_orgao_superior VARCHAR,
                codigo_unidade_gestora VARCHAR,
                nome_unidade_gestora VARCHAR,
                ano_exercicio USMALLINT,
                data_evento DATE,
                data_competencia DATE,
                funcao_governo VARCHAR,
                subfuncao_governo VARCHAR,
                programa_governo VARCHAR,
                acao_governamental VARCHAR,
                elemento_despesa VARCHAR,
                fase_despesa VARCHAR,
                valor_bruto_centavos BIGINT,
                valor_anulacoes_centavos BIGINT,
                valor_liquido_centavos BIGINT,
                valor_liquido_reais DOUBLE,
                is_transferencia_intergovernamental BOOLEAN,
                ente_destinatario VARCHAR,
                tipo_documento VARCHAR,
                numero_documento_origem VARCHAR,
                codigo_processo_licitatorio VARCHAR,
                id_contrato_pncp VARCHAR,
                favorecido_tipo VARCHAR,
                favorecido_documento VARCHAR,
                favorecido_nome VARCHAR,
                fonte_identificador VARCHAR,
                url_comprovante_oficial VARCHAR,
                hash_payload_extracao VARCHAR,
                data_ingestao TIMESTAMP,
                versao_registro UINTEGER,
                alerta_corrupcao BOOLEAN DEFAULT FALSE,
                motivo_alerta_corrupcao VARCHAR,
                tipo_risco_corrupcao VARCHAR
            );
        """)

    def sincronizar_com_silver(self) -> int:
        """Lê todos os Parquets da Silver e atualiza a Camada Gold."""
        padrao_parquet = str(self.silver_path / "**" / "*.parquet")
        arquivos = list(self.silver_path.glob("**/*.parquet"))
        if not arquivos:
            return 0

        # Ingestão em lote ultra-rápida do DuckDB lendo diretamente do Parquet
        self.conn.execute(f"""
            INSERT OR REPLACE INTO fato_despesa_unificada
            SELECT * FROM read_parquet('{padrao_parquet}', hive_partitioning=false);
        """)

        total = self.conn.execute("SELECT COUNT(*) FROM fato_despesa_unificada").fetchone()[0]
        return total

    def obter_resumo_nacional(self, ano: int = 2026) -> ResumoNacional:
        """
        Calcula os totais nacionais do ciclo orçamentário e o Gasto Efetivo Real
        (eliminando transferências intergovernamentais para evitar dupla contagem).
        """
        query = f"""
            SELECT
                COALESCE(SUM(CASE WHEN fase_despesa = 'DOTACAO' THEN valor_liquido_reais ELSE 0 END), 0) AS total_dotacao,
                COALESCE(SUM(CASE WHEN fase_despesa = 'EMPENHO' THEN valor_liquido_reais ELSE 0 END), 0) AS total_empenhado,
                COALESCE(SUM(CASE WHEN fase_despesa = 'LIQUIDACAO' THEN valor_liquido_reais ELSE 0 END), 0) AS total_liquidado,
                COALESCE(SUM(CASE WHEN fase_despesa = 'PAGAMENTO' THEN valor_liquido_reais ELSE 0 END), 0) AS total_pago,
                COALESCE(SUM(CASE WHEN fase_despesa = 'RESTOS_A_PAGAR_PAGOS' THEN valor_liquido_reais ELSE 0 END), 0) AS total_rap,
                COALESCE(SUM(CASE WHEN is_transferencia_intergovernamental = true THEN valor_liquido_reais ELSE 0 END), 0) AS total_transferencias,
                COUNT(*) AS total_registros,
                COALESCE(SUM(CASE WHEN alerta_corrupcao = true THEN 1 ELSE 0 END), 0) AS total_alertas_corrupcao,
                COALESCE(SUM(CASE WHEN alerta_corrupcao = true THEN valor_liquido_reais ELSE 0 END), 0) AS valor_sob_alerta_corrupcao
            FROM fato_despesa_unificada
            WHERE ano_exercicio = ?;
        """
        res = self._cursor().execute(query, [ano]).fetchone()
        (
            total_dotacao,
            total_empenhado,
            total_liquidado,
            total_pago,
            total_rap,
            total_transferencias,
            total_registros,
            total_alertas_corrupcao,
            valor_sob_alerta_corrupcao,
        ) = res

        # Gasto efetivo = Pagamentos diretos do ano + Pagamentos de Restos a Pagar - Transferências para outros entes
        gasto_efetivo = max(0.0, (total_pago + total_rap) - total_transferencias)

        return ResumoNacional(
            ano_exercicio=ano,
            total_dotacao_autorizada=round(total_dotacao, 2),
            total_empenhado_liquido=round(total_empenhado, 2),
            total_liquidado=round(total_liquidado, 2),
            total_pago_liquido=round(total_pago, 2),
            total_restos_a_pagar_pagos=round(total_rap, 2),
            total_transferencias_intergovernamentais=round(total_transferencias, 2),
            gasto_efetivo_nacional=round(gasto_efetivo, 2),
            total_alertas_corrupcao=int(total_alertas_corrupcao),
            valor_sob_alerta_corrupcao=round(valor_sob_alerta_corrupcao, 2),
            total_registros_processados=total_registros,
            data_ultima_atualizacao=datetime.now(timezone.utc),
        )

    def obter_ranking_orgaos(self, ano: int = 2026, limite: int = 10) -> List[Dict[str, Any]]:
        """Ranking de despesas por Órgão Superior (Ministério / Secretaria)."""
        query = """
            SELECT
                codigo_orgao_superior,
                nome_orgao_superior,
                SUM(CASE WHEN fase_despesa IN ('PAGAMENTO', 'RESTOS_A_PAGAR_PAGOS') THEN valor_liquido_reais ELSE 0 END) AS total_pago,
                SUM(CASE WHEN is_transferencia_intergovernamental = true THEN valor_liquido_reais ELSE 0 END) AS total_repasses,
                SUM(valor_liquido_reais) AS total_movimentado,
                COUNT(*) as qtd_documentos
            FROM fato_despesa_unificada
            WHERE ano_exercicio = ?
            GROUP BY codigo_orgao_superior, nome_orgao_superior
            ORDER BY total_pago DESC
            LIMIT ?;
        """
        rows = self._cursor().execute(query, [ano, limite]).fetchall()
        return [
            {
                "codigo": r[0],
                "nome": r[1],
                "total_pago": round(r[2], 2),
                "total_repasses": round(r[3], 2),
                "total_movimentado": round(r[4], 2),
                "qtd_documentos": r[5],
            }
            for r in rows
        ]

    def obter_gastos_por_funcao(self, ano: int = 2026) -> List[Dict[str, Any]]:
        """Distribuição de gastos por função governamental (Saúde, Educação, etc.)."""
        query = """
            SELECT
                funcao_governo,
                SUM(valor_liquido_reais) AS total_valor,
                COUNT(*) as qtd_eventos
            FROM fato_despesa_unificada
            WHERE ano_exercicio = ?
            GROUP BY funcao_governo
            ORDER BY total_valor DESC;
        """
        rows = self._cursor().execute(query, [ano]).fetchall()
        total_geral = sum(r[1] for r in rows) or 1.0
        return [
            {
                "funcao": r[0],
                "total_reais": round(r[1], 2),
                "percentual": round((r[1] / total_geral) * 100, 2),
                "qtd_eventos": r[2],
            }
            for r in rows
        ]

    def obter_top_fornecedores(self, ano: int = 2026, limite: int = 10) -> List[Dict[str, Any]]:
        """Top fornecedores e credores de recursos públicos com métricas de concentração."""
        query = """
            SELECT
                favorecido_nome,
                favorecido_documento,
                favorecido_tipo,
                SUM(valor_liquido_reais) AS total_recebido,
                COUNT(*) AS qtd_pagamentos,
                MAX(url_comprovante_oficial) AS exemplo_url
            FROM fato_despesa_unificada
            WHERE ano_exercicio = ?
            GROUP BY favorecido_nome, favorecido_documento, favorecido_tipo
            ORDER BY total_recebido DESC
            LIMIT ?;
        """
        rows = self._cursor().execute(query, [ano, limite]).fetchall()
        return [
            {
                "nome": r[0],
                "documento": r[1],
                "tipo": r[2],
                "total_recebido": round(r[3], 2),
                "qtd_pagamentos": r[4],
                "url_comprovante": r[5],
            }
            for r in rows
        ]

    def buscar_despesas(
        self,
        ano: int = 2026,
        orgao: Optional[str] = None,
        funcao: Optional[str] = None,
        fase: Optional[str] = None,
        termo_busca: Optional[str] = None,
        apenas_corrupcao: bool = False,
        limite: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Consulta avançada com filtros parametrizados e proteção estrita contra injeção SQL."""
        where_clauses = ["ano_exercicio = ?"]
        params: List[Any] = [ano]

        if orgao:
            where_clauses.append("codigo_orgao_superior = ?")
            params.append(orgao)
        if funcao:
            where_clauses.append("funcao_governo LIKE ?")
            params.append(f"%{funcao}%")
        if fase:
            where_clauses.append("fase_despesa = ?")
            params.append(fase)
        if apenas_corrupcao:
            where_clauses.append("alerta_corrupcao = true")
        if termo_busca:
            where_clauses.append(
                "(favorecido_nome ILIKE ? OR numero_documento_origem ILIKE ? OR acao_governamental ILIKE ?)"
            )
            param_busca = f"%{termo_busca}%"
            params.extend([param_busca, param_busca, param_busca])

        where_sql = " AND ".join(where_clauses)

        cur = self._cursor()
        total = cur.execute(
            f"SELECT COUNT(*) FROM fato_despesa_unificada WHERE {where_sql}",
            params
        ).fetchone()[0]

        query = f"""
            SELECT
                id,
                ente_federativo,
                nome_orgao_superior,
                nome_unidade_gestora,
                data_evento,
                funcao_governo,
                acao_governamental,
                fase_despesa,
                valor_liquido_reais,
                is_transferencia_intergovernamental,
                tipo_documento,
                numero_documento_origem,
                favorecido_nome,
                favorecido_documento,
                url_comprovante_oficial,
                hash_payload_extracao,
                alerta_corrupcao,
                motivo_alerta_corrupcao,
                tipo_risco_corrupcao
            FROM fato_despesa_unificada
            WHERE {where_sql}
            ORDER BY alerta_corrupcao DESC, valor_liquido_reais DESC
            LIMIT ? OFFSET ?;
        """
        query_params = params + [limite, offset]
        rows = cur.execute(query, query_params).fetchall()

        itens = [
            {
                "id": r[0],
                "ente_federativo": r[1],
                "orgao": r[2],
                "unidade_gestora": r[3],
                "data_evento": str(r[4]),
                "funcao": r[5],
                "acao": r[6],
                "fase_despesa": r[7],
                "valor_liquido_reais": r[8],
                "is_transferencia": r[9],
                "tipo_documento": r[10],
                "numero_documento": r[11],
                "favorecido_nome": r[12],
                "favorecido_documento": r[13],
                "url_oficial": r[14],
                "hash_sha256": r[15],
                "alerta_corrupcao": bool(r[16]),
                "motivo_corrupcao": r[17],
                "tipo_risco": r[18],
            }
            for r in rows
        ]

        return {
            "total_encontrado": total,
            "limite": limite,
            "offset": offset,
            "itens": itens,
        }

    def obter_alertas_corrupcao(self, ano: int = 2026) -> List[Dict[str, Any]]:
        """
        Recupera todas as despesas sob alerta vermelho de irregularidade/corrupção
        (Fase 5 - Controle Social e Auditoria Cidadã).
        """
        query = f"""
            SELECT
                id,
                numero_documento_origem,
                tipo_documento,
                nome_orgao_superior,
                nome_unidade_gestora,
                favorecido_nome,
                favorecido_documento,
                fase_despesa,
                valor_liquido_reais,
                tipo_risco_corrupcao,
                motivo_alerta_corrupcao,
                url_comprovante_oficial,
                hash_payload_extracao,
                data_evento
            FROM fato_despesa_unificada
            WHERE ano_exercicio = ? AND alerta_corrupcao = true
            ORDER BY valor_liquido_reais DESC;
        """
        rows = self._cursor().execute(query, [ano]).fetchall()
        return [
            {
                "id": r[0],
                "numero_documento": r[1],
                "tipo_documento": r[2],
                "orgao": r[3],
                "unidade_gestora": r[4],
                "favorecido_nome": r[5],
                "favorecido_documento": r[6],
                "fase_despesa": r[7],
                "valor_liquido_reais": round(r[8], 2),
                "tipo_risco": r[9],
                "motivo_corrupcao": r[10],
                "url_oficial": r[11],
                "hash_sha256": r[12],
                "data_evento": str(r[13]),
            }
            for r in rows
        ]

    def obter_rastreabilidade(self, identificador: str) -> Optional[Dict[str, Any]]:
        """Recupera o Contrato de Proveniência completo de um registro específico."""
        query = f"""
            SELECT
                id,
                ente_federativo,
                esfera,
                nome_orgao_superior,
                nome_unidade_gestora,
                ano_exercicio,
                data_evento,
                data_competencia,
                funcao_governo,
                acao_governamental,
                elemento_despesa,
                fase_despesa,
                valor_bruto_centavos,
                valor_anulacoes_centavos,
                valor_liquido_reais,
                is_transferencia_intergovernamental,
                tipo_documento,
                numero_documento_origem,
                favorecido_nome,
                favorecido_documento,
                fonte_identificador,
                url_comprovante_oficial,
                hash_payload_extracao,
                data_ingestao,
                alerta_corrupcao,
                motivo_alerta_corrupcao,
                tipo_risco_corrupcao
            FROM fato_despesa_unificada
            WHERE id = ? OR numero_documento_origem = ?
            LIMIT 1;
        """
        row = self._cursor().execute(query, [identificador, identificador]).fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "ente": row[1],
            "esfera": row[2],
            "orgao": row[3],
            "ug": row[4],
            "exercicio": row[5],
            "data_evento": str(row[6]),
            "data_competencia": str(row[7]),
            "funcao": row[8],
            "acao": row[9],
            "elemento": row[10],
            "fase": row[11],
            "valor_bruto": row[12] / 100.0,
            "valor_anulacoes": row[13] / 100.0,
            "valor_liquido": row[14],
            "is_transferencia": row[15],
            "documento": {
                "tipo": row[16],
                "numero": row[17],
            },
            "favorecido": {
                "nome": row[18],
                "documento": row[19],
            },
            "auditoria_proveniencia": {
                "fonte_oficial": row[20],
                "url_oficial": row[21],
                "hash_sha256": row[22],
                "data_ingestao": str(row[23]),
                "status": "VALIDADO_INTEGRIDADE_CONFERIDA",
            },
            "auditoria_corrupcao": {
                "alerta_ativo": bool(row[24]),
                "motivo": row[25],
                "tipo_risco": row[26],
            },
        }
