"""
Modelos canônicos de dados contábeis e fiscais do setor público brasileiro.
Conforme:
- Lei nº 4.320/1964 (Normas Gerais de Direito Financeiro)
- Lei de Responsabilidade Fiscal (LC nº 101/2000)
- Manual de Contabilidade Aplicada ao Setor Público (MCASP / STN)
"""

from enum import Enum
from typing import Optional
from datetime import date, datetime, timezone
from pydantic import BaseModel, Field, computed_field


class FaseDespesa(str, Enum):
    """Fases contábeis do ciclo da despesa pública brasileira."""
    DOTACAO = "DOTACAO"                        # Limite orçamentário autorizado
    EMPENHO = "EMPENHO"                        # Reserva formal de dotação (NE)
    LIQUIDACAO = "LIQUIDACAO"                  # Atesto de entrega do bem/serviço (NL)
    PAGAMENTO = "PAGAMENTO"                    # Desembolso financeiro efetivo (OB)
    RESTOS_A_PAGAR_PAGOS = "RESTOS_A_PAGAR_PAGOS" # Pagamento de compromisso de ano anterior


class EsferaGoverno(str, Enum):
    FEDERAL = "FEDERAL"
    ESTADUAL = "ESTADUAL"
    MUNICIPAL = "MUNICIPAL"


class PoderGoverno(str, Enum):
    EXECUTIVO = "EXECUTIVO"
    LEGISLATIVO = "LEGISLATIVO"
    JUDICIARIO = "JUDICIARIO"
    MINISTERIO_PUBLICO = "MINISTERIO_PUBLICO"
    DEFENSORIA_PUBLICA = "DEFENSORIA_PUBLICA"


class TipoFavorecido(str, Enum):
    PESSOA_JURIDICA = "PJ"
    PESSOA_FISICA = "PF"
    ENTE_PUBLICO = "ENTE_PUBLICO"
    SIGILOSO = "SIGILOSO"


class RegistroDespesaCanonica(BaseModel):
    """
    Registro unificado de despesa pública com rastreabilidade completa até a fonte.
    Armazena valores monetários em centavos (Int64) para prevenir imprecisão de float.
    """
    id: str = Field(..., description="UUID único do registro no sistema de transparência")
    ente_federativo: str = Field(..., description="Ex: 'UNIAO', 'ESTADO_SP', 'MUNICIPIO_3550308'")
    esfera: EsferaGoverno
    poder: PoderGoverno
    
    # Classificação Institucional
    codigo_orgao_superior: str = Field(..., description="Código do Ministério ou Secretaria")
    nome_orgao_superior: str
    codigo_unidade_gestora: str = Field(..., description="Código da UG (ex: SIAFI)")
    nome_unidade_gestora: str
    
    # Classificação Orçamentária e Funcional
    ano_exercicio: int
    data_evento: date
    data_competencia: date
    funcao_governo: str = Field(..., description="Ex: '10 - Saúde', '12 - Educação'")
    subfuncao_governo: str
    programa_governo: str
    acao_governamental: str
    elemento_despesa: str = Field(..., description="Ex: '33.90.30 - Material de Consumo'")
    
    # Ciclo da Despesa
    fase_despesa: FaseDespesa
    
    # Valores Monetários em Centavos (evita perda de precisão contábil)
    valor_bruto_centavos: int
    valor_anulacoes_centavos: int = 0
    
    # Tratamento da Bitributação / Transferências Intergovernamentais
    # Ex: Repasses fundo a fundo (FNS para FMS) ou cotas-parte (FPM/FPE)
    is_transferencia_intergovernamental: bool = Field(
        default=False,
        description="Verdadeiro se a despesa for repasse a outro ente federativo (evita dupla contagem nacional)"
    )
    ente_destinatario: Optional[str] = None
    
    # Linagem do Documento de Origem
    tipo_documento: str = Field(..., description="'NE' (Nota de Empenho), 'OB' (Ordem Bancária), etc.")
    numero_documento_origem: str
    codigo_processo_licitatorio: Optional[str] = None
    id_contrato_pncp: Optional[str] = None
    
    # Favorecido / Credor
    favorecido_tipo: TipoFavorecido
    favorecido_documento: str = Field(..., description="CNPJ completo ou CPF mascarado (ex: ***.123.456-**)")
    favorecido_nome: str
    
    # Proveniência & Auditoria
    fonte_identificador: str = Field(..., description="'PORTAL_TRANSPARENCIA_CGU', 'SICONFI', 'PNCP'")
    url_comprovante_oficial: str = Field(..., description="Link público direto para o documento na fonte governamental")
    hash_payload_extracao: str = Field(..., description="SHA-256 do arquivo bruto de onde o registro foi extraído")
    data_ingestao: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    versao_registro: int = 1

    # Alertas de Risco & Indícios de Corrupção (Fase 5 - Controle Social e Auditoria)
    alerta_corrupcao: bool = Field(
        default=False,
        description="Sinaliza indício grave de irregularidade, sobrepreço ou suspeita de corrupção (destacado em Vermelho)"
    )
    motivo_alerta_corrupcao: Optional[str] = Field(
        default=None,
        description="Fundamentação técnica do indício para auditoria do TCU / CGU / MPF"
    )
    tipo_risco_corrupcao: Optional[str] = Field(
        default=None,
        description="'EMPRESA_INIDONEA_CEIS', 'DISPENSA_SUSPEITA', 'FRACIONAMENTO_DESPESA', 'SOBREPRECO_ATIPICO'"
    )

    @computed_field
    @property
    def valor_liquido_centavos(self) -> int:
        return self.valor_bruto_centavos - self.valor_anulacoes_centavos

    @computed_field
    @property
    def valor_liquido_reais(self) -> float:
        return round(self.valor_liquido_centavos / 100.0, 2)


class ResumoNacional(BaseModel):
    """Consolidação nacional das métricas orçamentárias."""
    ano_exercicio: int
    total_dotacao_autorizada: float
    total_empenhado_liquido: float
    total_liquidado: float
    total_pago_liquido: float
    total_restos_a_pagar_pagos: float
    total_transferencias_intergovernamentais: float
    gasto_efetivo_nacional: float = Field(
        ...,
        description="Valor pago líquido menos transferências repassadas a outros entes (sem dupla contagem)"
    )
    total_alertas_corrupcao: int = Field(
        default=0,
        description="Total de despesas com indícios de corrupção ou irregularidades graves detectadas"
    )
    valor_sob_alerta_corrupcao: float = Field(
        default=0.0,
        description="Montante financeiro sob suspeita de sobrepreço ou corrupção (em Reais)"
    )
    total_registros_processados: int
    data_ultima_atualizacao: datetime
