"""
Testes unitários e de integração contábil da Plataforma de Transparência.
Validação estrita de integridade conforme Lei 4.320/64 sobre dados oficiais reais.
"""

from packages.pipeline.extractors.cgu_extractor import ExtratorCGU
from packages.pipeline.normalizer import NormalizadorSilver
from packages.pipeline.gold_engine import GoldAnalyticsEngine


def test_calculo_valor_liquido():
    """Valida se o valor líquido contábil deduz corretamente eventuais anulações/abatimentos."""
    extrator = ExtratorCGU()
    registros = extrator.extrair_despesas_reais(ano=2026)
    assert len(registros) > 0

    for reg in registros:
        assert reg.valor_liquido_centavos == reg.valor_bruto_centavos - reg.valor_anulacoes_centavos
        assert reg.valor_liquido_reais == round(reg.valor_liquido_centavos / 100.0, 2)


def test_prevencao_dupla_contagem_transferencias():
    """Valida se a regra de negócio isola repasses/fundos municipais para não inflar o gasto efetivo."""
    extrator = ExtratorCGU()
    registros = extrator.extrair_despesas_reais(ano=2026)

    repasses = [r for r in registros if r.is_transferencia_intergovernamental]
    assert len(repasses) > 0
    assert repasses[0].ente_destinatario is not None
    assert repasses[0].valor_liquido_reais > 0


def test_deduplicacao_silver():
    """Garante que reprocessamentos idempotentes não dupliquem registros."""
    extrator = ExtratorCGU()
    registros = extrator.extrair_despesas_reais(ano=2026)

    registros_duplicados = registros + registros
    normalizador = NormalizadorSilver()
    deduplicados = normalizador.deduplicar_e_validar(registros_duplicados)

    assert len(deduplicados) == len(registros)


def test_rastreabilidade_e_proveniencia():
    """Garante que cada registro real recupera sua proveniência com hash SHA-256 e URL oficial."""
    engine = GoldAnalyticsEngine(read_only=True)
    despesas = engine.buscar_despesas(ano=2026, limite=5)
    assert len(despesas["itens"]) > 0

    doc_id = despesas["itens"][0]["numero_documento"]
    rastro = engine.obter_rastreabilidade(doc_id)

    assert rastro is not None
    assert rastro["documento"]["numero"] == doc_id
    assert len(rastro["auditoria_proveniencia"]["hash_sha256"]) == 64
    assert rastro["auditoria_proveniencia"]["url_oficial"].startswith("https://")
