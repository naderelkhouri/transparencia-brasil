/**
 * Plataforma Transparência Brasil - Cliente Frontend
 * Tema: Cores do Brasil (Verde, Amarelo Ouro e Azul Noturno)
 * Regra: Vermelho EXCLUSIVAMENTE para sinalizar indícios de Corrupção e Irregularidades.
 */

// Formatador Monetário Brasileiro (BRL)
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 2,
  }).format(valor || 0);
};

const formatarNumero = (valor) => {
  return new Intl.NumberFormat('pt-BR').format(valor || 0);
};

// Estado da Aplicação
const state = {
  ano: 2026,
  modo: 'cidadao', // 'cidadao' | 'auditor'
  resumo: null,
  alertasCorrupcao: [],
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  inicializarEventos();
  carregarDadosCompletos();
});

function inicializarEventos() {
  // Alternador de Modo
  const btnCidadao = document.getElementById('btnModoCidadao');
  const btnAuditor = document.getElementById('btnModoAuditor');
  const funilSection = document.getElementById('funilOrcamentarioSection');

  btnCidadao.addEventListener('click', () => {
    state.modo = 'cidadao';
    btnCidadao.className = 'px-3 py-1.5 rounded-md transition-all bg-green-600 hover:bg-green-500 text-white font-bold shadow-sm';
    btnAuditor.className = 'px-3 py-1.5 rounded-md transition-all text-blue-200 hover:text-white';
    funilSection.classList.add('hidden');
  });

  btnAuditor.addEventListener('click', () => {
    state.modo = 'auditor';
    btnAuditor.className = 'px-3 py-1.5 rounded-md transition-all bg-yellow-500 hover:bg-yellow-400 text-blue-950 font-bold shadow-sm';
    btnCidadao.className = 'px-3 py-1.5 rounded-md transition-all text-blue-200 hover:text-white';
    funilSection.classList.remove('hidden');
  });

  // Botão direto para o Radar de Corrupção no topo
  document.getElementById('btnIrParaRadar').addEventListener('click', () => {
    navegarParaAba('tabRadarCorrupcao');
  });

  // Abas de Navegação
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      navegarParaAba(targetTab);
    });
  });

  // Botão Sincronizar Fontes
  document.getElementById('btnExecutarPipeline').addEventListener('click', async () => {
    const btn = document.getElementById('btnExecutarPipeline');
    btn.disabled = true;
    btn.innerHTML = '<span class="animate-spin inline-block mr-1">⚙️</span> Sincronizando...';
    try {
      await fetch(`/api/v1/pipeline/executar?ano=${state.ano}`, { method: 'POST' });
      await carregarDadosCompletos();
      alert('✅ Fontes sincronizadas com sucesso!');
    } catch (e) {
      alert('Erro ao sincronizar: ' + e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span class="inline-block w-2 h-2 rounded-full bg-yellow-400"></span> Sincronizar';
    }
  });

  // Busca Granular
  document.getElementById('btnBuscar').addEventListener('click', () => {
    const termo = document.getElementById('campoBusca').value;
    carregarDespesasGranulares(termo);
  });

  document.getElementById('campoBusca').addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
      carregarDespesasGranulares(e.target.value);
    }
  });

  // Fechar Modal
  document.getElementById('btnFecharModal').addEventListener('click', fecharModal);
  document.getElementById('btnFecharModalSecundario').addEventListener('click', fecharModal);
}

function navegarParaAba(targetTab) {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach((b) => {
    const isCorrupcao = b.getAttribute('data-tab') === 'tabRadarCorrupcao';
    b.classList.remove('active', 'border-yellow-400', 'text-yellow-400', 'bg-[#08182f]', 'border-red-500', 'text-red-400');
    if (!isCorrupcao) {
      b.classList.add('border-transparent', 'text-slate-400');
    }
  });

  const activeBtn = document.querySelector(`.tab-btn[data-tab="${targetTab}"]`);
  if (activeBtn) {
    if (targetTab === 'tabRadarCorrupcao') {
      activeBtn.classList.add('active', 'border-red-500', 'text-red-400');
    } else {
      activeBtn.classList.add('active', 'border-yellow-400', 'text-yellow-400', 'bg-[#08182f]');
      activeBtn.classList.remove('border-transparent', 'text-slate-400');
    }
  }

  document.querySelectorAll('.tab-content').forEach((sec) => sec.classList.add('hidden'));
  const targetSec = document.getElementById(targetTab);
  if (targetSec) {
    targetSec.classList.remove('hidden');
  }
}

async function carregarDadosCompletos() {
  await carregarResumoNacional();
  await Promise.all([
    carregarAlertasCorrupcao(),
    carregarOrgaos(),
    carregarFuncoes(),
    carregarMunicipios(),
    carregarContratosPNCP(),
    carregarTopFornecedores(),
    carregarDespesasGranulares(),
  ]);
}

// 1. Resumo Nacional e Funil
async function carregarResumoNacional() {
  try {
    const res = await fetch(`/api/v1/resumo?ano=${state.ano}`);
    const data = await res.json();
    state.resumo = data;

    // Atualiza KPIs
    document.getElementById('kpiGastoEfetivo').textContent = formatarMoeda(data.gasto_efetivo_nacional);
    document.getElementById('kpiTotalPago').textContent = formatarMoeda(data.total_pago_liquido);
    document.getElementById('kpiRapPagos').textContent = formatarMoeda(data.total_restos_a_pagar_pagos);
    document.getElementById('kpiTransferencias').textContent = formatarMoeda(data.total_transferencias_intergovernamentais);

    // KPI VERMELHO EXCLUSIVO: ALERTA DE CORRUPÇÃO
    const totalCorrupcao = data.total_alertas_corrupcao || 0;
    const valorCorrupcao = data.valor_sob_alerta_corrupcao || 0;

    document.getElementById('kpiTotalAlertasCorrupcao').textContent = `${totalCorrupcao} Casos`;
    document.getElementById('kpiValorCorrupcao').textContent = formatarMoeda(valorCorrupcao);
    document.getElementById('headerQtdCorrupcao').textContent = `${totalCorrupcao} Indícios`;

    // Atualiza Funil Orçamentário (se ativo)
    document.getElementById('funilEmpenho').textContent = formatarMoeda(data.total_empenhado_liquido);
    document.getElementById('funilLiquidado').textContent = formatarMoeda(data.total_liquidado);
    document.getElementById('funilPago').textContent = formatarMoeda(data.total_pago_liquido);
    document.getElementById('funilRepasses').textContent = formatarMoeda(data.total_transferencias_intergovernamentais);
  } catch (err) {
    console.error('Erro ao carregar resumo nacional:', err);
  }
}

// 2. RADAR ANTI-CORRUPÇÃO (DESTAQUE VERMELHO)
async function carregarAlertasCorrupcao() {
  const container = document.getElementById('gridCasosCorrupcao');
  try {
    const res = await fetch(`/api/v1/alertas-corrupcao?ano=${state.ano}`);
    const alertas = await res.json();
    state.alertasCorrupcao = alertas;

    if (!alertas || alertas.length === 0) {
      container.innerHTML = '<div class="col-span-3 py-6 text-center text-xs text-green-400">Nenhum indício grave registrado para o exercício.</div>';
      return;
    }

    container.innerHTML = alertas.map((a) => {
      let badgeRisco = 'EMPRESA INIDÔNEA (CEIS)';
      if (a.tipo_risco === 'SOBREPRECO_ATIPICO') badgeRisco = 'SOBREPREÇO ATÍPICO';
      if (a.tipo_risco === 'FRACIONAMENTO_ILEGAL') badgeRisco = 'FRACIONAMENTO ILEGAL';

      return `
        <div class="bg-[#1a0808] border-2 border-red-500/80 hover:border-red-400 rounded-xl p-4 flex flex-col justify-between space-y-3 transition-all shadow-xl shadow-red-950/40">
          <div class="space-y-2">
            <div class="flex items-center justify-between text-[11px]">
              <span class="badge-corrupcao font-mono">
                <span class="w-2 h-2 rounded-full bg-red-400 animate-ping"></span>
                ${badgeRisco}
              </span>
              <span class="text-red-300 font-mono text-[10px]">${a.data_evento}</span>
            </div>

            <div class="pt-1">
              <div class="text-[10px] uppercase tracking-wider text-red-300 font-bold">Valor sob Suspeita</div>
              <div class="text-xl font-black font-mono text-red-400">${formatarMoeda(a.valor_liquido_reais)}</div>
            </div>

            <div class="bg-red-950/60 p-2.5 rounded-lg border border-red-900/80 text-[11px] text-red-100 leading-snug">
              ${a.motivo_corrupcao}
            </div>

            <div class="text-[11px] space-y-0.5 text-blue-100">
              <div class="font-semibold text-white">${a.orgao}</div>
              <div class="text-blue-200/80 line-clamp-1">${a.unidade_gestora}</div>
              <div class="font-mono text-[10px] text-yellow-300 pt-1">
                Credor: ${a.favorecido_nome} (${a.favorecido_documento})
              </div>
            </div>
          </div>

          <div class="border-t border-red-900/60 pt-3 flex items-center justify-between">
            <span class="font-mono text-[11px] text-red-300 font-bold">${a.tipo_documento} nº ${a.numero_documento}</span>
            <button onclick="abrirModalRastreabilidade('${a.numero_documento}')" class="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-bold transition-all shadow-lg shadow-red-600/30">
              Auditar 🛡️
            </button>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = '<div class="col-span-3 py-4 text-center text-xs text-red-400">Erro ao carregar radar anti-corrupção.</div>';
  }
}

// 3. Ranking de Ministérios (Verde e Ouro)
async function carregarOrgaos() {
  const container = document.getElementById('listaOrgaos');
  try {
    const res = await fetch(`/api/v1/orgaos?ano=${state.ano}&limite=8`);
    const orgaos = await res.json();

    if (!orgaos || orgaos.length === 0) {
      container.innerHTML = '<div class="py-4 text-center text-xs text-slate-400">Nenhum órgão registrado.</div>';
      return;
    }

    container.innerHTML = orgaos.map((org, idx) => `
      <div class="py-3 flex items-center justify-between text-xs hover:bg-blue-900/30 px-2 rounded-lg transition-colors">
        <div class="flex items-center gap-3">
          <span class="w-6 h-6 rounded-full bg-blue-950 border border-yellow-400/40 flex items-center justify-center font-bold text-yellow-400 text-[11px] font-mono">
            ${idx + 1}
          </span>
          <div>
            <div class="font-semibold text-white">${org.nome}</div>
            <div class="text-[11px] text-blue-200/70 flex items-center gap-2">
              <span>Cód: ${org.codigo}</span>
              ${org.total_repasses > 0 ? `<span class="text-cyan-400">• Repasses: ${formatarMoeda(org.total_repasses)}</span>` : ''}
            </div>
          </div>
        </div>
        <div class="text-right">
          <div class="font-bold font-mono text-green-400">${formatarMoeda(org.total_pago)}</div>
          <div class="text-[10px] text-blue-200/60">${org.qtd_documentos} docs</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="py-4 text-center text-xs text-red-400">Erro ao carregar ministérios.</div>';
  }
}

// 4. Funções de Governo
async function carregarFuncoes() {
  const container = document.getElementById('listaFuncoes');
  try {
    const res = await fetch(`/api/v1/funcoes?ano=${state.ano}`);
    const funcoes = await res.json();

    container.innerHTML = funcoes.map((f) => `
      <div class="space-y-1 text-xs">
        <div class="flex justify-between items-center text-blue-100">
          <span class="font-semibold">${f.funcao}</span>
          <span class="font-mono text-white font-bold">${formatarMoeda(f.total_reais)} <span class="text-yellow-400 text-[11px]">(${f.percentual}%)</span></span>
        </div>
        <div class="w-full bg-blue-950 rounded-full h-2.5 overflow-hidden border border-blue-900">
          <div class="bg-gradient-to-r from-green-600 via-green-500 to-yellow-400 h-2.5 rounded-full" style="width: ${Math.min(100, f.percentual)}%"></div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="py-4 text-center text-xs text-red-400">Erro ao carregar funções.</div>';
  }
}

// 5. Estados e Municípios (SICONFI)
async function carregarMunicipios() {
  const tbody = document.getElementById('tabelaMunicipios');
  try {
    const res = await fetch(`/api/v1/siconfi/municipios?ano=${state.ano}`);
    const munics = await res.json();

    tbody.innerHTML = munics.map((m) => `
      <tr class="hover:bg-blue-900/30 transition-colors">
        <td class="py-3 px-3 font-semibold text-white">
          ${m.municipio} - <span class="text-yellow-400 font-bold">${m.uf}</span>
          <div class="text-[10px] text-blue-300 font-mono">IBGE: ${m.codigo_ibge}</div>
        </td>
        <td class="py-3 px-3 font-mono text-blue-100">${formatarNumero(m.populacao_ibge)} hab.</td>
        <td class="py-3 px-3 font-mono font-bold text-green-400">${formatarMoeda(m.gasto_per_capita)} / hab</td>
        <td class="py-3 px-3 font-mono text-blue-200">${formatarMoeda(m.gasto_saude)}</td>
        <td class="py-3 px-3 font-mono text-blue-200">${formatarMoeda(m.gasto_educacao)}</td>
        <td class="py-3 px-3 font-mono font-semibold text-white">${formatarMoeda(m.despesa_paga)}</td>
        <td class="py-3 px-3 text-right">
          <a href="${m.fonte_url}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1 bg-blue-950 hover:bg-blue-900 text-yellow-400 border border-yellow-500/40 rounded text-[11px] font-semibold transition-colors">
            SICONFI ↗
          </a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-xs text-red-400">Erro ao carregar municípios.</td></tr>';
  }
}

// 6. Contratos do PNCP
async function carregarContratosPNCP() {
  const container = document.getElementById('cardsContratos');
  try {
    const res = await fetch(`/api/v1/pncp/contratos?ano=${state.ano}`);
    const contratos = await res.json();

    container.innerHTML = contratos.map((c) => `
      <div class="bg-[#0b1b33] border border-blue-900 rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-yellow-400/50 transition-all">
        <div class="space-y-2">
          <div class="flex items-center justify-between text-[11px]">
            <span class="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono">
              Contrato nº ${c.numero_contrato}
            </span>
            <span class="text-blue-300 font-mono text-[10px]">${c.vigencia_inicio} a ${c.vigencia_fim}</span>
          </div>
          <h4 class="text-xs font-semibold text-white line-clamp-2 leading-snug">
            ${c.objeto}
          </h4>
          <div class="text-[11px] text-blue-200/80">
            <span class="block text-white font-medium">${c.orgao_nome}</span>
            <span class="block text-yellow-300 font-mono text-[10px]">Credor: ${c.fornecedor_razao_social}</span>
          </div>
        </div>

        <div class="border-t border-blue-900/80 pt-2 flex items-center justify-between">
          <div>
            <div class="text-[10px] uppercase text-blue-300">Homologado</div>
            <div class="text-sm font-bold font-mono text-green-400">${formatarMoeda(c.valor_homologado)}</div>
          </div>
          <a href="${c.url_oficial}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1 bg-blue-950 hover:bg-blue-900 text-yellow-400 border border-yellow-500/40 rounded text-[11px] font-bold transition-colors">
            Ver PNCP ↗
          </a>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="col-span-3 py-4 text-center text-xs text-red-400">Erro ao carregar contratos do PNCP.</div>';
  }
}

// 7. Top Fornecedores
async function carregarTopFornecedores() {
  const tbody = document.getElementById('tabelaFornecedores');
  try {
    const res = await fetch(`/api/v1/fornecedores?ano=${state.ano}&limite=10`);
    const fornecedores = await res.json();

    tbody.innerHTML = fornecedores.map((f) => `
      <tr class="hover:bg-blue-900/30 transition-colors">
        <td class="py-3 px-3 font-semibold text-white">${f.nome}</td>
        <td class="py-3 px-3 font-mono text-blue-200">${f.documento}</td>
        <td class="py-3 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-950 text-blue-200 border border-blue-800">
            ${f.tipo}
          </span>
        </td>
        <td class="py-3 px-3 font-mono text-blue-200">${f.qtd_pagamentos}</td>
        <td class="py-3 px-3 font-mono font-bold text-green-400">${formatarMoeda(f.total_recebido)}</td>
        <td class="py-3 px-3 text-right">
          <a href="${f.url_comprovante}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1 bg-blue-950 hover:bg-blue-900 text-yellow-400 border border-yellow-500/40 rounded text-[11px] font-semibold transition-colors">
            Consultar ↗
          </a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-xs text-red-400">Erro ao carregar fornecedores.</td></tr>';
  }
}

// 8. Despesas Granulares com Destaque Vermelho em Corrupção
async function carregarDespesasGranulares(termo = '') {
  const tbody = document.getElementById('tabelaDespesas');
  try {
    let url = `/api/v1/despesas?ano=${state.ano}&limite=20`;
    if (termo) url += `&busca=${encodeURIComponent(termo)}`;

    const res = await fetch(url);
    const data = await res.json();

    if (!data.itens || data.itens.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-xs text-slate-400">Nenhum registro encontrado para a busca.</td></tr>';
      return;
    }

    tbody.innerHTML = data.itens.map((d) => {
      let badgeClass = 'badge-pagamento';
      if (d.fase_despesa === 'EMPENHO') badgeClass = 'badge-empenho';
      if (d.fase_despesa === 'LIQUIDACAO') badgeClass = 'badge-liquidacao';
      if (d.fase_despesa === 'RESTOS_A_PAGAR_PAGOS') badgeClass = 'badge-rap';

      // Linha em Vermelho se houver Alerta de Corrupção
      const linhaClasse = d.alerta_corrupcao ? 'linha-corrupcao' : 'hover:bg-blue-900/30';

      return `
        <tr class="${linhaClasse} transition-colors">
          <td class="py-3 px-3">
            <span class="font-mono font-bold text-white">${d.numero_documento}</span>
            <div class="text-[10px] text-blue-300 font-mono">${d.tipo_documento}</div>
          </td>
          <td class="py-3 px-3 font-mono text-blue-200/80 text-[11px]">${d.data_evento}</td>
          <td class="py-3 px-3">
            <div class="font-semibold text-white">${d.orgao}</div>
            <div class="text-[11px] text-blue-200/70 line-clamp-1">${d.unidade_gestora}</div>
          </td>
          <td class="py-3 px-3">
            <div class="font-semibold text-white">${d.favorecido_nome}</div>
            <div class="text-[11px] text-yellow-300 font-mono">${d.favorecido_documento}</div>
          </td>
          <td class="py-3 px-3">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="badge-fase ${badgeClass}">${d.fase_despesa}</span>
              ${d.is_transferencia ? '<span class="badge-fase badge-repasse">REPASSE</span>' : ''}
              ${d.alerta_corrupcao ? `
                <span class="badge-corrupcao text-[10px] font-mono">
                  🚨 CORRUPÇÃO / RISCO
                </span>
              ` : ''}
            </div>
          </td>
          <td class="py-3 px-3 font-mono font-bold ${d.alerta_corrupcao ? 'text-red-400' : 'text-green-400'}">
            ${formatarMoeda(d.valor_liquido_reais)}
          </td>
          <td class="py-3 px-3 text-right">
            <button onclick="abrirModalRastreabilidade('${d.numero_documento}')" class="px-2.5 py-1 ${d.alerta_corrupcao ? 'bg-red-600 hover:bg-red-500 text-white border-red-500' : 'bg-green-600/20 hover:bg-green-600/40 text-green-300 border-green-500/40'} border rounded text-[11px] font-bold transition-colors">
              ${d.alerta_corrupcao ? 'Auditar 🚨' : 'Rastrear 🛡️'}
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-xs text-red-400">Erro ao carregar despesas.</td></tr>';
  }
}

// 9. Modal de Rastreabilidade & Proveniência com Destaque de Corrupção
async function abrirModalRastreabilidade(docId) {
  const modal = document.getElementById('modalRastreabilidade');
  const conteudo = document.getElementById('conteudoModal');
  modal.classList.remove('hidden');

  conteudo.innerHTML = `
    <div class="py-8 text-center">
      <div class="animate-spin text-2xl mb-2">⚙️</div>
      <p class="text-blue-200">Consultando linagem contábil e hash SHA-256 do documento ${docId}...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/v1/rastreabilidade/${docId}`);
    if (!res.ok) throw new Error('Documento não encontrado');
    const rastro = await res.json();

    const temAlertaCorrupcao = rastro.auditoria_corrupcao && rastro.auditoria_corrupcao.alerta_ativo;

    conteudo.innerHTML = `
      <div class="space-y-4">
        
        <!-- BANNER VERMELHO SE HOUVER INDÍCIO DE CORRUPÇÃO -->
        ${temAlertaCorrupcao ? `
          <div class="bg-red-950/90 border-2 border-red-500 p-4 rounded-xl space-y-2 shadow-2xl shadow-red-900/40">
            <div class="flex items-center justify-between text-red-300 font-extrabold text-xs uppercase tracking-wide">
              <span class="flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
                <span>🚨 INDÍCIO DE CORRUPÇÃO / IRREGULARIDADE GRAVE DETECTADO</span>
              </span>
              <span class="text-[10px] font-mono bg-red-600 text-white px-2 py-0.5 rounded">ALERTA AUDITORIA</span>
            </div>
            <p class="text-white text-xs font-semibold leading-relaxed">
              ${rastro.auditoria_corrupcao.motivo}
            </p>
            <div class="text-[10px] text-red-200 font-mono">
              Classificação do Risco: <strong>${rastro.auditoria_corrupcao.tipo_risco}</strong> • Encaminhar denúncia aos órgãos de controle (TCU / CGU / MPF)
            </div>
          </div>
        ` : ''}

        <!-- Resumo do Documento -->
        <div class="bg-[#030a16] p-4 rounded-xl border border-blue-900 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs uppercase tracking-wider text-blue-300 font-semibold">Documento Oficial</span>
            <span class="font-mono text-yellow-400 font-bold">${rastro.documento.tipo} nº ${rastro.documento.numero}</span>
          </div>
          <div class="text-xl font-black ${temAlertaCorrupcao ? 'text-red-400' : 'text-green-400'} font-mono">
            ${formatarMoeda(rastro.valor_liquido)}
          </div>
          <div class="text-xs text-blue-100">
            <strong>Fase Contábil:</strong> ${rastro.fase}
            ${rastro.is_transferencia ? ' • <span class="text-cyan-400 font-semibold">Repasse Intergovernamental (Fundo a Fundo)</span>' : ''}
          </div>
        </div>

        <!-- Órgão e Favorecido -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-blue-950/60 p-3 rounded-lg border border-blue-900">
            <div class="text-[10px] uppercase text-blue-300 font-bold">Órgão Emissor</div>
            <div class="font-semibold text-white mt-1">${rastro.orgao}</div>
            <div class="text-[11px] text-blue-200/70 font-mono mt-0.5">${rastro.ug}</div>
          </div>
          <div class="bg-blue-950/60 p-3 rounded-lg border border-blue-900">
            <div class="text-[10px] uppercase text-blue-300 font-bold">Favorecido / Credor</div>
            <div class="font-semibold text-white mt-1">${rastro.favorecido.nome}</div>
            <div class="text-[11px] text-yellow-300 font-mono mt-0.5">${rastro.favorecido.documento}</div>
          </div>
        </div>

        <!-- Proveniência Forense & Integridade Criptográfica -->
        <div class="bg-blue-950/40 border border-blue-800 p-3.5 rounded-xl space-y-2">
          <div class="flex items-center justify-between text-yellow-400 text-xs font-semibold">
            <span>🛡️ Rastreabilidade Oficial (Lei 12.527 / LAI)</span>
            <span class="text-[10px] font-mono bg-green-950 text-green-300 border border-green-500/40 px-2 py-0.5 rounded">STATUS: AUTÊNTICO</span>
          </div>
          <div class="space-y-1 text-[11px] text-blue-100">
            <div><strong>Fonte Oficial:</strong> ${rastro.auditoria_proveniencia.fonte_oficial}</div>
            <div class="break-all font-mono text-[10px] text-blue-300">
              <strong>Hash SHA-256 do Arquivo de Extração:</strong><br>
              ${rastro.auditoria_proveniencia.hash_sha256}
            </div>
            <div class="text-blue-200/70 text-[10px]">
              <strong>Data de Extração:</strong> ${rastro.auditoria_proveniencia.data_ingestao}
            </div>
          </div>
        </div>

        <!-- Ação Oficial -->
        <div class="pt-1">
          <a href="${rastro.auditoria_proveniencia.url_oficial}" target="_blank" rel="noopener noreferrer" class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-green-600 hover:bg-green-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-green-600/25 text-xs">
            <span>Ver Comprovante Oficial no Portal da Transparência</span>
            <span>↗</span>
          </a>
        </div>
      </div>
    `;
  } catch (err) {
    conteudo.innerHTML = `<div class="py-4 text-center text-red-400">${err.message}</div>`;
  }
}

function fecharModal() {
  document.getElementById('modalRastreabilidade').classList.add('hidden');
}

// Expõe funções globais para manipulação de eventos inline
window.abrirModalRastreabilidade = abrirModalRastreabilidade;
window.navegarParaAba = navegarParaAba;
