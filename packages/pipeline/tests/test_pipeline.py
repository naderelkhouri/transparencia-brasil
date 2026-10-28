"""
Testes unitários e de integração contábil da Plataforma de Transparência.
Validação estrita de integridade conforme Lei 4.320/64.
"""

import pytest
from packages.pipeline.models import (
    RegistroDespesaCanonica,
    FaseDespesa,
    EsferaGoverno,
    PoderGoverno,
    TipoFavorecido,
)
from packages.pipeline.extractors.cgu_extractor import ExtratorCGU
from packages.pipeline.normalizer import NormalizadorSilver
from packages.pipeline.gold_engine import GoldAnalyticsEngine


def test_calculo_valor_liquido():
    """Valida se o valor líquido contábil deduz corretamente as anulações de empenho."""
    extrator = ExtratorCGU()
    registros = extrator.gerar_lote_oficial_realista(ano=2026)

    # Registro de obra rodoviária do DNIT tem R$ 85M bruto e R$ 5M de anulação
    reg_dnit = next(r for r in registros if "DNIT" in r.nome_unidade_gestora)
    assert reg_dnit.valor_bruto_centavos == 85_000_000_00
    assert reg_dnit.valor_anulacoes_centavos == 5_000_000_00
    assert reg_dnit.valor_liquido_centavos == 80_000_000_00
    assert reg_dnit.valor_liquido_reais == 80_000_000.00


def test_prevencao_dupla_contagem_transferencias():
    """Valida se a regra de negócio isola repasses FNS para não inflar o gasto efetivo."""
    extrator = ExtratorCGU()
    registros = extrator.gerar_lote_oficial_realista(ano=2026)

    repasse_saude = next(r for r in registros if r.is_transferencia_intergovernamental)
    assert repasse_saude.ente_destinatario == "MUNICIPIO_3550308_SP"
    assert repasse_saude.valor_liquido_reais == 120_000_000.00


def test_deduplicacao_silver():
    """Garante que reprocessamentos idempotentes não dupliquem registros."""
    extrator = ExtratorCGU()
    registros = extrator.gerar_lote_oficial_realista(ano=2026)

    # Duplica a lista propositalmente
    registros_duplicados = registros + registros

    normalizador = NormalizadorSilver()
    deduplicados = normalizador.deduplicar_e_validar(registros_duplicados)

    assert len(deduplicados) == len(registros)


def test_rastreabilidade_e_proveniencia():
    """Garante que cada registro recupera sua proveniência com hash SHA-256 e URL oficial."""
    engine = GoldAnalyticsEngine()
    engine.sincronizar_com_silver()

    # Consulta por documento oficial da OB de vacinas
    doc_id = "2026OB800142"
    rastro = engine.obter_rastreabilidade(doc_id)

    assert rastro is not None
    assert rastro["documento"]["numero"] == doc_id
    assert rastro["auditoria_proveniencia"]["fonte_oficial"] == "PORTAL_TRANSPARENCIA_CGU"
    assert len(rastro["auditoria_proveniencia"]["hash_sha256"]) == 64
    assert "portaldatransparencia.gov.br" in rastro["auditoria_proveniencia"]["url_oficial"]
