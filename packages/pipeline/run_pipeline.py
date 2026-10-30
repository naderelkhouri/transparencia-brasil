"""
Script de Orquestração do Pipeline de Ingestão e Processamento.
Executa o ciclo Medallion (Bronze ➔ Silver ➔ Gold).
"""

import sys
import time
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from packages.pipeline.extractors.cgu_extractor import ExtratorCGU
from packages.pipeline.extractors.siconfi_extractor import ExtratorSiconfi
from packages.pipeline.extractors.pncp_extractor import ExtratorPNCP
from packages.pipeline.normalizer import NormalizadorSilver
from packages.pipeline.gold_engine import GoldAnalyticsEngine


def executar_pipeline(ano: int = 2026):
    inicio = time.time()
    print("=" * 70)
    print(f"🚀 INICIANDO PIPELINE DE TRANSPARÊNCIA PÚBLICA BRASIL (ANO {ano})")
    print("=" * 70)

    # 1. Camada Bronze: Extração Direta das APIs Oficiais (Sem Dados Mockados)
    print("\n[1/3] 📥 Extraindo dados reais das APIs governamentais oficiais (Bronze)...")
    extrator_cgu = ExtratorCGU()
    registros_cgu = extrator_cgu.extrair_despesas_reais(ano=ano)
    print(f"  ✓ Despesas/Contratos/TCU consolidados: {len(registros_cgu)} registros oficiais extraídos")

    extrator_siconfi = ExtratorSiconfi()
    dados_siconfi = extrator_siconfi.obter_dados_municipios_reais(ano=ano)
    print(f"  ✓ SICONFI (Tesouro Nacional - RREO): {len(dados_siconfi)} capitais consolidadas")

    extrator_pncp = ExtratorPNCP()
    dados_pncp = extrator_pncp.obter_contratos_reais(ano=ano)
    print(f"  ✓ PNCP (Contratações Públicas): {len(dados_pncp)} contratos oficiais")

    # 2. Camada Silver: Normalização e Parquet
    print("\n[2/3] ⚙️  Normalizando, deduplicando e gravando Parquet (Silver)...")
    normalizador = NormalizadorSilver()
    arquivos_parquet = normalizador.salvar_parquet(registros_cgu)
    for arq in arquivos_parquet:
        print(f"  ✓ Arquivo Parquet gerado: {arq}")

    # 3. Camada Gold: Carga Analítica
    print("\n[3/3] 🏛️  Carregando tabelas analíticas materializadas (Gold)...")
    engine = GoldAnalyticsEngine(read_only=False)
    total_carregado = engine.sincronizar_com_silver()
    print(f"  ✓ Total de registros analíticos sincronizados na Gold: {total_carregado}")

    # Resumo Contábil
    resumo = engine.obter_resumo_nacional(ano=ano)
    tempo_total = time.time() - inicio

    print("\n" + "=" * 70)
    print("📊 RESULTADO DA EXECUÇÃO DO CICLO ORÇAMENTÁRIO (LEI 4.320/64)")
    print("=" * 70)
    print(f"  • Total Empenhado Líquido:       R$ {resumo.total_empenhado_liquido:,.2f}")
    print(f"  • Total Liquidado:               R$ {resumo.total_liquidado:,.2f}")
    print(f"  • Total Pago Líquido (Exercício): R$ {resumo.total_pago_liquido:,.2f}")
    print(f"  • Restos a Pagar Pagos (RAP):    R$ {resumo.total_restos_a_pagar_pagos:,.2f}")
    print(f"  • Transferências (Repasses FMS): R$ {resumo.total_transferencias_intergovernamentais:,.2f}")
    print(f"  ─────────────────────────────────────────────────────────────────")
    print(f"  💎 GASTO EFETIVO NACIONAL LÍQUIDO: R$ {resumo.gasto_efetivo_nacional:,.2f}")
    print(f"     (Exclui transferências intergovernamentais para evitar dupla contagem)")
    print(f"  ⏱️  Tempo total de processamento: {tempo_total:.3f} segundos")
    print("=" * 70 + "\n")

    return resumo


if __name__ == "__main__":
    executar_pipeline()
