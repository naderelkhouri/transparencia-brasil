/**
 * Plataforma Transparência Brasil - Cliente Frontend
 * Tema: Sóbrio em Fundo Branco (Papel Neutro, Azul Institucional, Verde Bandeira, Âmbar Ouro)
 * Regra: Vermelho EXCLUSIVAMENTE para sinalizar indícios de Corrupção e Irregularidades Graves.
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

// Ícone SVG de Link Externo
const svgExternalLink = `
  <svg class="w-3 h-3 inline-block ml-1 opacity-70" viewBox="0 0 20 20" fill="currentColor">
    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"/>
    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"/>
  </svg>
`;

// Ícone SVG de Alerta de Corrupção
const svgAlertTriangle = `
  <svg class="w-3.5 h-3.5 text-red-600 shrink-0 inline-block" viewBox="0 0 20 20" fill="currentColor">
    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
  </svg>
`;

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
    btnCidadao.className = 'min-h-9 px-3 py-1.5 bg-slate-900 text-white font-bold transition-colors whitespace-nowrap';
    btnAuditor.className = 'min-h-9 px-3 py-1.5 bg-white text-slate-700 hover:text-slate-900 font-semibold transition-colors whitespace-nowrap';
    funilSection.classList.add('hidden');
  });

  btnAuditor.addEventListener('click', () => {
    state.modo = 'auditor';
    btnAuditor.className = 'min-h-9 px-3 py-1.5 bg-[#002776] text-white font-bold transition-colors whitespace-nowrap';
    btnCidadao.className = 'min-h-9 px-3 py-1.5 bg-white text-slate-700 hover:text-slate-900 font-semibold transition-colors whitespace-nowrap';
    funilSection.classList.remove('hidden');
  });

  // Botão direto para o Radar de Corrupção no topo
  document.getElementById('btnIrParaRadar').addEventListener('click', () => {
    navegarParaAba('tabRadarCorrupcao');
  });

  // Abas de Navegação (Sidebar)
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      navegarParaAba(targetTab);
    });
  });

  // Abas da Barra Inferior Mobile
  const mobileBtns = document.querySelectorAll('[data-mobile-tab]');
  mobileBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-mobile-tab');
      navegarParaAba(targetTab);
    });
  });

  // Controle do Drawer Lateral Mobile
  const btnAbrirSidebar = document.getElementById('btnAbrirSidebar');
  const btnFecharSidebar = document.getElementById('btnFecharSidebar');
  const btnMenuMobileInferior = document.getElementById('btnMenuMobileInferior');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  if (btnAbrirSidebar) btnAbrirSidebar.addEventListener('click', abrirSidebarMobile);
  if (btnMenuMobileInferior) btnMenuMobileInferior.addEventListener('click', abrirSidebarMobile);
  if (btnFecharSidebar) btnFecharSidebar.addEventListener('click', fecharSidebarMobile);
  if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', fecharSidebarMobile);

  // Botão Sincronizar Fontes
  document.getElementById('btnExecutarPipeline').addEventListener('click', async () => {
    const btn = document.getElementById('btnExecutarPipeline');
    btn.disabled = true;
    btn.innerHTML = `
      <svg class="animate-spin inline-block mr-1.5 w-3.5 h-3.5 text-slate-700" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Sincronizando...
    `;
    try {
      await fetch(`/api/v1/pipeline/executar?ano=${state.ano}`, { method: 'POST' });
      await carregarDadosCompletos();
      console.log('Fontes sincronizadas com sucesso.');
    } catch (e) {
      console.error('Erro ao sincronizar:', e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span class="inline-block w-2 h-2 rounded-full bg-[#00853b]"></span> Sincronizar';
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

  const checkCorrupcao = document.getElementById('checkApenasCorrupcao');
  if (checkCorrupcao) {
    checkCorrupcao.addEventListener('change', () => {
      const termo = document.getElementById('campoBusca').value;
      carregarDespesasGranulares(termo);
    });
  }

  // Fechar Modal
  document.getElementById('btnFecharModal').addEventListener('click', fecharModal);
  document.getElementById('btnFecharModalSecundario').addEventListener('click', fecharModal);
}

function abrirSidebarMobile() {
  const sidebar = document.getElementById('appSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  if (sidebar) sidebar.classList.remove('-translate-x-full');
  if (backdrop) backdrop.classList.remove('hidden');
}

function fecharSidebarMobile() {
  const sidebar = document.getElementById('appSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  if (sidebar) sidebar.classList.add('-translate-x-full');
  if (backdrop) backdrop.classList.add('hidden');
}

function navegarParaAba(targetTab) {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach((b) => {
    const isCorrupcao = b.getAttribute('data-tab') === 'tabRadarCorrupcao';
    b.classList.remove('active', 'font-bold');
    if (!isCorrupcao) {
      b.classList.add('text-slate-600');
    }
  });

  const activeBtn = document.querySelector(`.tab-btn[data-tab="${targetTab}"]`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'font-bold');
    activeBtn.classList.remove('text-slate-600');
  }

  // Sincroniza Barra Inferior Mobile
  const mobileBtns = document.querySelectorAll('[data-mobile-tab]');
  mobileBtns.forEach((mb) => {
    mb.classList.remove('active');
    if (mb.getAttribute('data-mobile-tab') === targetTab) {
      mb.classList.add('active');
    }
  });

  document.querySelectorAll('.tab-content').forEach((sec) => sec.classList.add('hidden'));
  const targetSec = document.getElementById(targetTab);
  if (targetSec) {
    targetSec.classList.remove('hidden');
  }

  // Fecha o drawer caso esteja aberto no mobile
  fecharSidebarMobile();
}

async function carregarDadosCompletos() {
  await carregarResumoNacional();
  await Promise.all([
    carregarAlertasCorrupcao(),
    carregarEconomiaPlanoVsRealidade(),
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
    const tabQtd = document.getElementById('tabQtdCorrupcao');
    if (tabQtd) tabQtd.textContent = `${totalCorrupcao} Casos`;

    // Atualiza Funil Orçamentário
    document.getElementById('funilEmpenho').textContent = formatarMoeda(data.total_empenhado_liquido);
    document.getElementById('funilLiquidado').textContent = formatarMoeda(data.total_liquidado);
    document.getElementById('funilPago').textContent = formatarMoeda(data.total_pago_liquido);
    document.getElementById('funilRepasses').textContent = formatarMoeda(data.total_transferencias_intergovernamentais);
  } catch (err) {
    console.error('Erro ao carregar resumo nacional:', err);
  }
}

// 2. Mapeador de Enquadramento Legal e Órgãos Competentes (Legal Compliance Checker)
function obterEnquadramentoLegal(tipoRisco) {
  if (tipoRisco === 'EMPRESA_PUNIDA_CEIS') {
    return {
      badge: 'EMPRESA INIDÔNEA (CEIS/TCU)',
      leiCurta: 'Lei nº 14.133/2021 (Art. 156, IV) & Lei nº 12.846/2013',
      fundamentoCompleto: 'Art. 156, inciso IV da Lei nº 14.133/2021 (Nova Lei de Licitações - Declaração de Inidoneidade), Lei nº 12.846/2013 (Lei Anticorrupção Empresarial) e Art. 46 da Lei nº 8.443/1992 (Lei Orgânica do TCU).',
      orgaosDestino: 'TCU (Ouvidoria), CGU (Fala.BR) e MPF (2ª/5ª Câmara)',
    };
  }
  if (tipoRisco === 'FRACIONAMENTO_ILEGAL') {
    return {
      badge: 'RETENÇÃO / PARALISIA ORÇAMENTÁRIA',
      leiCurta: 'LC nº 101/2000 (LRF Art. 9º e 42) & Lei nº 4.320/1964',
      fundamentoCompleto: 'Lei Complementar nº 101/2000 (Lei de Responsabilidade Fiscal - Art. 9º e Art. 42 sobre limitação de empenho e inscrição atípica em Restos a Pagar), Art. 36 da Lei nº 4.320/1964 e Art. 37 da Constituição Federal (Princípio da Eficiência Administrativa).',
      orgaosDestino: 'TCU (Contas da União), MPF (Procuradoria dos Direitos do Cidadão) e Congresso Nacional (CMO)',
    };
  }
  return {
    badge: 'DESVIO FISCAL / EXECUÇÃO CRÍTICA',
    leiCurta: 'Lei nº 8.429/1992 (Art. 10/11) & CF/88 Art. 70/74 § 2º',
    fundamentoCompleto: 'Art. 70 e Art. 74, § 2º da Constituição Federal de 1988, Lei Complementar nº 101/2000 (LRF - Responsabilidade na Gestão Fiscal) e Lei nº 8.429/1992 (Improbidade Administrativa e Lesão ao Erário).',
    orgaosDestino: 'MPF (5ª Câmara - Patrimônio Público), TCU e CGU',
  };
}

// 2A. RADAR ANTI-CORRUPÇÃO (DESTAQUE VERMELHO EM FUNDO BRANCO)
async function carregarAlertasCorrupcao() {
  const container = document.getElementById('gridCasosCorrupcao');
  try {
    const res = await fetch(`/api/v1/alertas-corrupcao?ano=${state.ano}`);
    const alertas = await res.json();
    state.alertasCorrupcao = alertas;

    if (!alertas || alertas.length === 0) {
      container.innerHTML = '<div class="col-span-3 py-6 text-center text-xs text-emerald-700">Nenhum indício grave registrado para o exercício.</div>';
      return;
    }

    // Ordena rigorosamente pelos valores mais elevados primeiro
    alertas.sort((x, y) => (Number(y.valor_liquido_reais) || 0) - (Number(x.valor_liquido_reais) || 0));

    container.innerHTML = alertas.map((a, idx) => {
      const legal = obterEnquadramentoLegal(a.tipo_risco);

      return `
        <div class="bg-white border border-red-200 hover:border-red-400 rounded-xl p-4 flex flex-col justify-between space-y-3 transition-all shadow-xs">
          <div class="space-y-2.5">
            <div class="flex items-center justify-between gap-2 text-xs">
              <span class="badge-corrupcao">
                ${svgAlertTriangle}
                <span>#${idx + 1} • ${legal.badge}</span>
              </span>
              <span class="text-red-800 font-mono text-xs tabular-nums font-bold whitespace-nowrap">${a.data_evento}</span>
            </div>

            <div class="pt-0.5">
              <div class="text-xs uppercase tracking-wider text-red-800 font-bold">Valor sob Auditoria / Suspeita</div>
              <div class="text-xl font-black font-mono tabular-nums text-red-700 whitespace-nowrap">${formatarMoeda(a.valor_liquido_reais)}</div>
            </div>

            <p class="text-xs text-slate-800 leading-relaxed font-medium">
              ${a.motivo_corrupcao}
            </p>

            <!-- Pílula de Tipificação Legal e Órgão Competente -->
            <div class="p-2.5 rounded-lg bg-red-50 border border-red-200 space-y-1 text-xs">
              <div class="font-bold text-red-900 flex items-center gap-1.5">
                <span>⚖️ Base Legal:</span>
                <span class="font-mono font-semibold text-red-800">${legal.leiCurta}</span>
              </div>
              <div class="text-red-800">
                <strong>Reportar a:</strong> ${legal.orgaosDestino}
              </div>
            </div>

            <div class="text-xs space-y-0.5 text-slate-600">
              <div class="font-bold text-slate-900 text-balance">${a.orgao}</div>
              <div class="text-slate-600 line-clamp-1">${a.unidade_gestora}</div>
              <div class="font-mono text-xs text-amber-800 font-semibold pt-1">
                Credor: ${a.favorecido_nome} <span class="whitespace-nowrap">(${a.favorecido_documento})</span>
              </div>
            </div>
          </div>

          <div class="border-t border-red-100 pt-3 flex items-center justify-between gap-2">
            <span class="font-mono text-xs text-red-800 font-bold tabular-nums whitespace-nowrap">${a.tipo_documento} nº ${a.numero_documento}</span>
            <button onclick="abrirModalRastreabilidade('${a.numero_documento}')" class="min-h-9 px-3.5 py-1.5 bg-[#dc2626] hover:bg-[#b91c1c] text-white rounded-lg text-xs font-bold transition-all shadow-xs whitespace-nowrap">
              Denunciar / Auditar
            </button>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = '<div class="col-span-3 py-4 text-center text-xs text-red-600">Erro ao carregar radar anti-corrupção.</div>';
  }
}

// 2B. ECONOMIA: PLANO DE GOVERNO VS. REALIDADE EXECUTADA (BCB + SICONFI UNIÃO)
async function carregarEconomiaPlanoVsRealidade() {
  const gridMacro = document.getElementById('gridIndicadoresEconomia');
  const tbodySetorial = document.getElementById('tabelaEconomiaSetorial');
  if (!gridMacro || !tbodySetorial) return;

  try {
    const res = await fetch(`/api/v1/economia/plano-vs-realidade?ano=${state.ano}`);
    const data = await res.json();

    // Renderiza Indicadores Macroeconômicos (BCB SGS + Tesouro)
    const macro = data.indicadores_macro || [];
    gridMacro.innerHTML = macro.map((m) => `
      <div class="bg-white border border-red-200 rounded-xl p-4 flex flex-col justify-between space-y-3 shadow-xs">
        <div class="space-y-2">
          <div class="flex items-center justify-between gap-2 text-xs">
            <span class="badge-corrupcao">${svgAlertTriangle}<span>DESVIO DE META</span></span>
            <span class="font-mono text-xs font-semibold text-slate-600 tabular-nums whitespace-nowrap">${m.data_referencia}</span>
          </div>
          <h4 class="text-sm font-bold text-slate-900 leading-snug text-balance">${m.indicador}</h4>
          <div class="space-y-1.5 pt-1 text-xs">
            <div class="flex items-baseline justify-between gap-2">
              <span class="text-slate-600 font-medium">Plano Prometido:</span>
              <span class="font-mono font-bold text-emerald-800 tabular-nums whitespace-nowrap">${m.plano_prometido}</span>
            </div>
            <div class="flex items-baseline justify-between gap-2">
              <span class="text-slate-600 font-medium">Realidade em Prática:</span>
              <span class="font-mono font-black text-red-700 tabular-nums text-sm whitespace-nowrap">${m.realidade_pratica}</span>
            </div>
            <div class="text-xs font-mono font-bold text-red-800 pt-0.5">
              ${m.desvio_critico}
            </div>
          </div>
          <p class="text-xs text-slate-700 leading-relaxed pt-1">
            ${m.impacto_real}
          </p>
        </div>
        <div class="border-t border-red-100 pt-2.5 flex items-center justify-between gap-2 text-xs">
          <span class="font-mono text-xs text-slate-600 truncate max-w-[180px]">${m.fonte_oficial}</span>
          <a href="${m.url_comprovante}" target="_blank" rel="noopener noreferrer" class="min-h-8 px-2 py-1 text-[#002776] font-bold hover:underline inline-flex items-center whitespace-nowrap">
            Fonte Oficial ${svgExternalLink}
          </a>
        </div>
      </div>
    `).join('');

    // Renderiza Comparativo Setorial da União (Ordenado pelos Valores Mais Elevados)
    const setores = (data.comparativo_setorial || []).sort(
      (a, b) => (Number(b.orcamento_planejado_reais) || 0) - (Number(a.orcamento_planejado_reais) || 0)
    );

    tbodySetorial.innerHTML = setores.map((s) => {
      const linhaClasse = s.alerta_grave ? 'linha-corrupcao' : 'hover:bg-slate-50';
      const corPct = s.alerta_grave ? 'text-red-700 font-black' : 'text-emerald-800 font-bold';
      return `
        <tr class="${linhaClasse} transition-colors">
          <td data-label="Função / Promessa" class="py-3 px-4">
            <div>
              <div class="font-bold text-slate-900 text-balance">${s.funcao}</div>
              <div class="text-xs text-slate-600">${s.promessa_plano}</div>
            </div>
          </td>
          <td data-label="Planejado (LOA)" class="py-3 px-4 text-right font-mono tabular-nums font-semibold text-slate-900 whitespace-nowrap">
            ${formatarMoeda(s.orcamento_planejado_reais)}
          </td>
          <td data-label="Executado" class="py-3 px-4 text-right font-mono tabular-nums font-bold text-emerald-800 whitespace-nowrap">
            ${formatarMoeda(s.executado_efetivo_reais)}
          </td>
          <td data-label="% Entregue" class="py-3 px-4 text-right font-mono tabular-nums whitespace-nowrap ${corPct}">
            ${s.taxa_execucao_pct.toFixed(1)}%
          </td>
          <td data-label="Travado em RAP" class="py-3 px-4 text-right font-mono tabular-nums font-bold whitespace-nowrap ${s.alerta_grave ? 'text-red-700' : 'text-amber-800'}">
            ${formatarMoeda(s.travado_restos_a_pagar_reais)}
          </td>
          <td data-label="Diagnóstico" class="py-3 px-4 text-xs leading-relaxed ${s.alerta_grave ? 'text-red-800 font-semibold' : 'text-slate-700'}">
            <span>${s.diagnostico_auditoria}</span>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Erro ao carregar economia plano vs realidade:', err);
  }
}

// 3. Ranking de Ministérios
async function carregarOrgaos() {
  const container = document.getElementById('listaOrgaos');
  try {
    const res = await fetch(`/api/v1/orgaos?ano=${state.ano}&limite=8`);
    const orgaos = await res.json();

    if (!orgaos || orgaos.length === 0) {
      container.innerHTML = '<div class="py-4 text-center text-xs text-slate-500">Nenhum órgão registrado.</div>';
      return;
    }

    container.innerHTML = orgaos.map((org, idx) => `
      <div class="py-3 flex items-center justify-between gap-3 text-xs hover:bg-slate-50 px-2 rounded-lg transition-colors">
        <div class="flex items-center gap-3">
          <span class="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-[#002776] text-xs font-mono tabular-nums shrink-0">
            ${idx + 1}
          </span>
          <div>
            <div class="font-bold text-slate-900 text-balance">${org.nome}</div>
            <div class="text-xs text-slate-600 flex items-center gap-2 flex-wrap">
              <span class="whitespace-nowrap">Cód: ${org.codigo}</span>
              ${org.total_repasses > 0 ? `<span class="text-sky-800 font-semibold whitespace-nowrap">• Repasses: ${formatarMoeda(org.total_repasses)}</span>` : ''}
            </div>
          </div>
        </div>
        <div class="text-right shrink-0 whitespace-nowrap">
          <div class="font-bold font-mono tabular-nums text-emerald-800">${formatarMoeda(org.total_pago)}</div>
          <div class="text-xs text-slate-600 font-semibold tabular-nums">${org.qtd_documentos} docs</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="py-4 text-center text-xs text-red-600">Erro ao carregar ministérios.</div>';
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
        <div class="flex justify-between items-baseline gap-2 text-slate-700">
          <span class="font-semibold text-slate-900">${f.funcao}</span>
          <span class="font-mono tabular-nums text-slate-900 font-bold whitespace-nowrap">${formatarMoeda(f.total_reais)} <span class="text-[#002776] text-xs font-bold">(${f.percentual}%)</span></span>
        </div>
        <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
          <div class="bg-[#00853b] h-2 rounded-full" style="width: ${Math.min(100, f.percentual)}%"></div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="py-4 text-center text-xs text-red-600">Erro ao carregar funções.</div>';
  }
}

// 5. Estados e Municípios (SICONFI)
async function carregarMunicipios() {
  const tbody = document.getElementById('tabelaMunicipios');
  try {
    const res = await fetch(`/api/v1/siconfi/municipios?ano=${state.ano}`);
    const munics = await res.json();

    tbody.innerHTML = munics.map((m) => `
      <tr class="hover:bg-slate-50 transition-colors">
        <td data-label="Município / UF" class="py-3 px-4 font-semibold text-slate-900 whitespace-nowrap">
          <div>
            ${m.municipio} - <span class="text-[#002776] font-bold">${m.uf}</span>
            <div class="text-xs text-slate-600 font-mono tabular-nums">IBGE: ${m.codigo_ibge}</div>
          </div>
        </td>
        <td data-label="População" class="py-3 px-4 font-mono tabular-nums text-slate-700 text-right whitespace-nowrap">${formatarNumero(m.populacao_ibge)} hab.</td>
        <td data-label="Gasto per Capita" class="py-3 px-4 text-right">
          <div class="inline-flex items-baseline justify-end gap-1 whitespace-nowrap font-mono tabular-nums">
            <span class="font-extrabold text-sm text-emerald-800">${formatarMoeda(m.gasto_per_capita)}</span>
            <span class="text-xs font-semibold text-slate-600">/hab</span>
          </div>
        </td>
        <td data-label="Saúde" class="py-3 px-4 font-mono tabular-nums text-slate-700 text-right whitespace-nowrap">${formatarMoeda(m.gasto_saude)}</td>
        <td data-label="Educação" class="py-3 px-4 font-mono tabular-nums text-slate-700 text-right whitespace-nowrap">${formatarMoeda(m.gasto_educacao)}</td>
        <td data-label="Total Pago" class="py-3 px-4 font-mono tabular-nums font-bold text-slate-900 text-right whitespace-nowrap">${formatarMoeda(m.despesa_paga)}</td>
        <td data-label="Comprovante" class="py-3 px-4 text-right">
          <a href="${m.fonte_url}" target="_blank" rel="noopener noreferrer" class="min-h-8 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-[#002776] border border-slate-200 rounded-lg text-xs font-bold transition-colors inline-flex items-center whitespace-nowrap">
            SICONFI ${svgExternalLink}
          </a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-xs text-red-600">Erro ao carregar municípios.</td></tr>';
  }
}

// 6. Contratos do PNCP
async function carregarContratosPNCP() {
  const container = document.getElementById('cardsContratos');
  try {
    const res = await fetch(`/api/v1/pncp/contratos?ano=${state.ano}`);
    const contratos = await res.json();

    container.innerHTML = contratos.map((c) => `
      <div class="bg-white border border-slate-200 rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-slate-300 transition-all shadow-xs">
        <div class="space-y-2">
          <div class="flex items-center justify-between gap-2 text-xs">
            <span class="px-2 py-0.5 rounded bg-slate-100 text-[#002776] border border-slate-200 font-mono tabular-nums font-bold whitespace-nowrap">
              Contrato nº ${c.numero_contrato}
            </span>
            <span class="text-slate-600 font-mono text-xs font-semibold tabular-nums whitespace-nowrap">${c.vigencia_inicio} a ${c.vigencia_fim}</span>
          </div>
          <h4 class="text-sm font-bold text-slate-900 line-clamp-2 leading-snug text-balance">
            ${c.objeto}
          </h4>
          <div class="text-xs text-slate-600 space-y-0.5">
            <span class="block text-slate-900 font-semibold text-balance">${c.orgao_nome}</span>
            <span class="block text-amber-800 font-mono text-xs font-semibold">Credor: ${c.fornecedor_razao_social}</span>
          </div>
        </div>

        <div class="border-t border-slate-100 pt-2.5 flex items-center justify-between gap-2">
          <div class="whitespace-nowrap">
            <div class="text-xs font-bold uppercase tracking-wider text-slate-600">Homologado</div>
            <div class="text-sm sm:text-base font-extrabold font-mono tabular-nums text-emerald-800">${formatarMoeda(c.valor_homologado)}</div>
          </div>
          <a href="${c.url_oficial}" target="_blank" rel="noopener noreferrer" class="min-h-8 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-[#002776] border border-slate-200 rounded-lg text-xs font-bold transition-colors inline-flex items-center whitespace-nowrap">
            Ver PNCP ${svgExternalLink}
          </a>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="col-span-3 py-4 text-center text-xs text-red-600">Erro ao carregar contratos do PNCP.</div>';
  }
}

// 7. Top Fornecedores
async function carregarTopFornecedores() {
  const tbody = document.getElementById('tabelaFornecedores');
  try {
    const res = await fetch(`/api/v1/fornecedores?ano=${state.ano}&limite=10`);
    const fornecedores = await res.json();

    tbody.innerHTML = fornecedores.map((f) => `
      <tr class="hover:bg-slate-50 transition-colors">
        <td data-label="Credor / Nome" class="py-3 px-4 font-semibold text-slate-900"><span>${f.nome}</span></td>
        <td data-label="CNPJ / CPF" class="py-3 px-4 font-mono tabular-nums text-slate-700 whitespace-nowrap">${f.documento}</td>
        <td data-label="Tipo" class="py-3 px-4 whitespace-nowrap">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap">
            ${f.tipo}
          </span>
        </td>
        <td data-label="Ordens Bancárias" class="py-3 px-4 text-right font-mono tabular-nums text-slate-700 whitespace-nowrap">${f.qtd_pagamentos}</td>
        <td data-label="Total Recebido" class="py-3 px-4 text-right font-mono tabular-nums font-bold text-emerald-800 whitespace-nowrap">${formatarMoeda(f.total_recebido)}</td>
        <td data-label="Rastrear" class="py-3 px-4 text-right">
          <a href="${f.url_comprovante}" target="_blank" rel="noopener noreferrer" class="min-h-8 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-[#002776] border border-slate-200 rounded-lg text-xs font-bold transition-colors inline-flex items-center whitespace-nowrap">
            Consultar ${svgExternalLink}
          </a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-xs text-red-600">Erro ao carregar fornecedores.</td></tr>';
  }
}

// 8. Despesas Granulares com Destaque Vermelho em Corrupção
async function carregarDespesasGranulares(termo = '') {
  const tbody = document.getElementById('tabelaDespesas');
  const checkCorrupcao = document.getElementById('checkApenasCorrupcao');
  const apenasCorrupcao = checkCorrupcao ? checkCorrupcao.checked : false;

  // Atualiza link de exportação de dados abertos CSV
  const linkCsv = document.getElementById('linkExportarCsv');
  if (linkCsv) {
    linkCsv.href = `/api/v1/exportar/despesas.csv?ano=${state.ano}&apenas_corrupcao=${apenasCorrupcao}`;
  }

  try {
    let url = `/api/v1/despesas?ano=${state.ano}&limite=50&apenas_corrupcao=${apenasCorrupcao}`;
    if (termo) url += `&busca=${encodeURIComponent(termo)}`;

    const res = await fetch(url);
    const data = await res.json();

    if (!data.itens || data.itens.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-xs text-slate-500">Nenhum registro encontrado para a busca.</td></tr>';
      return;
    }

    tbody.innerHTML = data.itens.map((d) => {
      let badgeClass = 'badge-pagamento';
      if (d.fase_despesa === 'EMPENHO') badgeClass = 'badge-empenho';
      if (d.fase_despesa === 'LIQUIDACAO') badgeClass = 'badge-liquidacao';
      if (d.fase_despesa === 'RESTOS_A_PAGAR_PAGOS') badgeClass = 'badge-rap';

      // Linha em Vermelho se houver Alerta de Corrupção
      const linhaClasse = d.alerta_corrupcao ? 'linha-corrupcao' : 'hover:bg-slate-50';

      return `
        <tr class="${linhaClasse} transition-colors">
          <td data-label="Doc / Tipo" class="py-3 px-4 whitespace-nowrap">
            <div>
              <span class="font-mono tabular-nums font-bold text-slate-900">${d.numero_documento}</span>
              <div class="text-xs text-slate-600 font-mono font-semibold">${d.tipo_documento}</div>
            </div>
          </td>
          <td data-label="Data" class="py-3 px-4 font-mono tabular-nums text-slate-700 text-xs whitespace-nowrap">${d.data_evento}</td>
          <td data-label="Órgão / UG" class="py-3 px-4">
            <div>
              <div class="font-semibold text-slate-900 text-balance">${d.orgao}</div>
              <div class="text-xs text-slate-600 line-clamp-1">${d.unidade_gestora}</div>
            </div>
          </td>
          <td data-label="Favorecido" class="py-3 px-4">
            <div>
              <div class="font-semibold text-slate-900">${d.favorecido_nome}</div>
              <div class="text-xs text-amber-800 font-mono tabular-nums whitespace-nowrap">${d.favorecido_documento}</div>
            </div>
          </td>
          <td data-label="Fase & Alerta" class="py-3 px-4">
            <div class="flex items-center justify-end md:justify-start gap-1.5 flex-wrap">
              <span class="badge-fase ${badgeClass}">${d.fase_despesa}</span>
              ${d.is_transferencia ? '<span class="badge-fase badge-repasse">REPASSE</span>' : ''}
              ${d.alerta_corrupcao ? `
                <span class="badge-corrupcao text-xs font-mono">
                  ${svgAlertTriangle}
                  <span>CORRUPÇÃO / RISCO</span>
                </span>
              ` : ''}
            </div>
          </td>
          <td data-label="Valor Líquido" class="py-3 px-4 text-right font-mono tabular-nums font-bold whitespace-nowrap ${d.alerta_corrupcao ? 'text-red-700' : 'text-emerald-800'}">
            ${formatarMoeda(d.valor_liquido_reais)}
          </td>
          <td data-label="Proveniência" class="py-3 px-4 text-right">
            <button onclick="abrirModalRastreabilidade('${d.numero_documento}')" class="min-h-8 px-3 py-1.5 ${d.alerta_corrupcao ? 'bg-[#dc2626] hover:bg-[#b91c1c] text-white border-red-600' : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-emerald-300'} border rounded-lg text-xs font-bold transition-colors whitespace-nowrap">
              ${d.alerta_corrupcao ? 'Auditar' : 'Rastrear'}
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-xs text-red-600">Erro ao carregar despesas.</td></tr>';
  }
}

// 9. Modal de Rastreabilidade & Proveniência com Destaque de Corrupção
async function abrirModalRastreabilidade(docId) {
  const modal = document.getElementById('modalRastreabilidade');
  const conteudo = document.getElementById('conteudoModal');
  modal.classList.remove('hidden');

  conteudo.innerHTML = `
    <div class="py-8 text-center">
      <svg class="animate-spin inline-block w-6 h-6 text-[#002776] mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-slate-600 text-xs">Consultando linagem contábil e hash SHA-256 do documento ${docId}...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/v1/rastreabilidade/${docId}`);
    if (!res.ok) throw new Error('Documento não encontrado');
    const rastro = await res.json();

    const temAlertaCorrupcao = rastro.auditoria_corrupcao && rastro.auditoria_corrupcao.alerta_ativo;
    const legal = obterEnquadramentoLegal(temAlertaCorrupcao ? rastro.auditoria_corrupcao.tipo_risco : 'REGULAR');

    const textoPeticao = [
      'EXCELENTÍSSIMO(A) SENHOR(A) PROCURADOR(A) DA REPÚBLICA (MPF) / AUDITOR(A) DO TRIBUNAL DE CONTAS DA UNIÃO (TCU) / OUVIDORIA-GERAL DA UNIÃO (CGU)',
      '',
      'ASSUNTO: REPRESENTAÇÃO CIDADÃ E NOTÍCIA DE FATO — INDÍCIO DE IRREGULARIDADE / DESVIO NA EXECUÇÃO DA DESPESA PÚBLICA',
      '',
      '1. LEGITIMIDADE CONSTITUCIONAL:',
      'Nos termos do Art. 5º, inciso XXXIV, alínea "a", e do Art. 74, § 2º da Constituição Federal de 1988 ("qualquer cidadão, partido político, associação ou sindicato é parte legítima para, na forma da lei, denunciar irregularidades ou ilegalidades perante o Tribunal de Contas da União"), apresento a presente Notícia de Fato instruída com prova criptográfica de dados abertos governamentais.',
      '',
      '2. IDENTIFICAÇÃO DO REGISTRO AUDITADO:',
      `• Documento Oficial: ${rastro.documento.tipo} nº ${rastro.documento.numero} (Exercício ${rastro.documento.ano})`,
      `• Valor Auditado: ${formatarMoeda(rastro.valor_liquido)} (${rastro.fase})`,
      `• Órgão / Unidade Gestora: ${rastro.orgao} — ${rastro.ug}`,
      `• Favorecido / Credor: ${rastro.favorecido.nome} (CNPJ/CPF: ${rastro.favorecido.documento})`,
      '',
      '3. FATO / ANOMALIA DETECTADA:',
      `${temAlertaCorrupcao ? rastro.auditoria_corrupcao.motivo : 'Solicitação de verificação de conformidade da execução física e financeira do gasto público.'}`,
      '',
      '4. ENQUADRAMENTO E TIPIFICAÇÃO LEGAL:',
      `• ${legal.fundamentoCompleto}`,
      '• Lei nº 12.527/2011 (Lei de Acesso à Informação - Art. 7º, VI e Art. 8º) e Lei nº 4.320/1964 (arts. 62 e 63 - Liquidação e Pagamento).',
      '',
      '5. PROVA DE INTEGRIDADE E RASTREABILIDADE (CADEIA DE CUSTÓDIA):',
      `• Fonte Oficial Primária: ${rastro.auditoria_proveniencia.fonte_oficial}`,
      `• URL de Verificação Pública: ${rastro.auditoria_proveniencia.url_oficial}`,
      `• Hash Criptográfico SHA-256: ${rastro.auditoria_proveniencia.hash_sha256}`,
      `• Timestamp de Extração: ${rastro.auditoria_proveniencia.data_ingestao}`,
      '',
      '6. PEDIDO:',
      'Requer-se a instauração de procedimento apuratório / auditoria especial para verificação da regularidade da aplicação dos recursos públicos acima identificados, bem como a responsabilização dos agentes públicos e terceiros beneficiados em caso de confirmação de lesão ao erário (Lei nº 8.429/1992 e Lei nº 12.846/2013).',
    ].join('\n');

    window.__ultimaPeticaoTexto = textoPeticao;

    conteudo.innerHTML = `
      <div class="space-y-4">
        
        <!-- BANNER VERMELHO SE HOUVER INDÍCIO DE CORRUPÇÃO -->
        ${temAlertaCorrupcao ? `
          <div class="bg-red-50 border border-red-300 p-4 rounded-xl space-y-2 shadow-xs">
            <div class="flex items-center justify-between gap-2 text-red-800 font-extrabold text-xs uppercase tracking-wide flex-wrap">
              <span class="flex items-center gap-1.5">
                ${svgAlertTriangle}
                <span>INDÍCIO DE CORRUPÇÃO / IRREGULARIDADE GRAVE DETECTADO</span>
              </span>
              <span class="text-xs font-mono bg-[#dc2626] text-white px-2.5 py-0.5 rounded font-bold whitespace-nowrap">ALERTA AUDITORIA</span>
            </div>
            <p class="text-red-900 text-xs font-semibold leading-relaxed">
              ${rastro.auditoria_corrupcao.motivo}
            </p>
            <div class="text-xs text-red-800 font-mono font-semibold pt-1 border-t border-red-200">
              <strong>⚖️ Enquadramento Legal:</strong> ${legal.fundamentoCompleto}
            </div>
          </div>
        ` : ''}

        <!-- GERADOR AUTOMÁTICO DE REPRESENTAÇÃO / NOTÍCIA DE FATO (ZERO ATRITO PARA O CIDADÃO) -->
        <div class="bg-white border-2 border-[#002776] p-4 rounded-xl space-y-3 shadow-xs">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div class="text-xs font-extrabold uppercase tracking-wider text-[#002776]">
                ⚡ Passo 2 & 3: Peça de Denúncia Pronta para Protocolo
              </div>
              <p class="text-xs text-slate-600">
                Copie a Notícia de Fato abaixo (já com base legal e Hash SHA-256) e cole no canal oficial escolhido:
              </p>
            </div>
            <button type="button" id="btnCopiarPeticao" onclick="copiarPeticaoAtual()" class="min-h-10 px-4 py-2 bg-[#dc2626] hover:bg-[#b91c1c] text-white font-bold rounded-lg text-xs transition-all shadow-xs whitespace-nowrap">
              📋 Copiar Denúncia Formal
            </button>
          </div>

          <textarea id="textareaPeticaoLegal" readonly rows="7" class="w-full bg-slate-50 border border-slate-300 rounded-lg p-3 font-mono text-base sm:text-xs text-slate-800 leading-relaxed focus:outline-none">${textoPeticao}</textarea>

          <!-- Botões Diretos para os 3 Órgãos Públicos Responsáveis -->
          <div class="space-y-1.5 pt-1">
            <div class="text-xs font-bold text-slate-800">
              Canais Oficiais de Recebimento de Denúncia (Clique para abrir o protocolo):
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <a href="https://www.mpf.mp.br/mpfservicos" target="_blank" rel="noopener noreferrer" class="min-h-10 px-3 py-2 bg-[#002776] hover:bg-blue-900 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors whitespace-nowrap">
                <span>1. Protocolar no MPF</span>
                ${svgExternalLink}
              </a>
              <a href="https://falabr.cgu.gov.br/" target="_blank" rel="noopener noreferrer" class="min-h-10 px-3 py-2 bg-[#00853b] hover:bg-[#006b2f] text-white rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors whitespace-nowrap">
                <span>2. Ouvidoria CGU (Fala.BR)</span>
                ${svgExternalLink}
              </a>
              <a href="https://portal.tcu.gov.br/ouvidoria/" target="_blank" rel="noopener noreferrer" class="min-h-10 px-3 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors whitespace-nowrap">
                <span>3. Denunciar ao TCU</span>
                ${svgExternalLink}
              </a>
            </div>
          </div>
        </div>

        <!-- Resumo do Documento -->
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs uppercase tracking-wider text-slate-600 font-bold">Documento Oficial</span>
            <span class="font-mono tabular-nums text-[#002776] font-bold whitespace-nowrap">${rastro.documento.tipo} nº ${rastro.documento.numero}</span>
          </div>
          <div class="text-xl font-black ${temAlertaCorrupcao ? 'text-red-700' : 'text-emerald-800'} font-mono tabular-nums whitespace-nowrap">
            ${formatarMoeda(rastro.valor_liquido)}
          </div>
          <div class="text-xs text-slate-700">
            <strong>Fase Contábil:</strong> ${rastro.fase}
            ${rastro.is_transferencia ? ' • <span class="text-sky-800 font-semibold">Repasse Intergovernamental (Fundo a Fundo)</span>' : ''}
          </div>
        </div>

        <!-- Órgão e Favorecido -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <div class="text-xs uppercase tracking-wider text-slate-600 font-bold">Órgão Emissor</div>
            <div class="font-semibold text-slate-900 mt-1 text-balance">${rastro.orgao}</div>
            <div class="text-xs text-slate-600 font-mono mt-0.5">${rastro.ug}</div>
          </div>
          <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <div class="text-xs uppercase tracking-wider text-slate-600 font-bold">Favorecido / Credor</div>
            <div class="font-semibold text-slate-900 mt-1">${rastro.favorecido.nome}</div>
            <div class="text-xs text-amber-800 font-mono tabular-nums mt-0.5 whitespace-nowrap">${rastro.favorecido.documento}</div>
          </div>
        </div>

        <!-- Proveniência Forense & Integridade Criptográfica -->
        <div class="bg-slate-50 border border-slate-200 p-3.5 rounded-xl space-y-2">
          <div class="flex items-center justify-between gap-2 text-[#002776] text-xs font-bold flex-wrap">
            <span>Rastreabilidade Oficial (Lei nº 12.527 / LAI)</span>
            <span class="text-xs font-mono bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded font-bold whitespace-nowrap">STATUS: AUTÊNTICO</span>
          </div>
          <div class="space-y-1 text-xs text-slate-700">
            <div><strong>Fonte Oficial:</strong> ${rastro.auditoria_proveniencia.fonte_oficial}</div>
            <div class="break-all font-mono text-xs text-slate-600">
              <strong>Hash SHA-256 do Registro:</strong><br>
              ${rastro.auditoria_proveniencia.hash_sha256}
            </div>
            <div class="text-slate-600 text-xs tabular-nums">
              <strong>Data de Extração:</strong> ${rastro.auditoria_proveniencia.data_ingestao}
            </div>
          </div>
        </div>

        <!-- Ação Oficial -->
        <div class="pt-1">
          <a href="${rastro.auditoria_proveniencia.url_oficial}" target="_blank" rel="noopener noreferrer" class="min-h-11 w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl transition-all shadow-xs text-xs whitespace-nowrap">
            <span>Conferir Registro Bruto na Fonte Oficial do Governo</span>
            ${svgExternalLink}
          </a>
        </div>
      </div>
    `;
  } catch (err) {
    conteudo.innerHTML = `<div class="py-4 text-center text-red-600">${err.message}</div>`;
  }
}

function fecharModal() {
  document.getElementById('modalRastreabilidade').classList.add('hidden');
}

function copiarPeticaoAtual() {
  const texto = window.__ultimaPeticaoTexto || '';
  const btn = document.getElementById('btnCopiarPeticao');
  if (navigator.clipboard && texto) {
    navigator.clipboard.writeText(texto).then(() => {
      if (btn) {
        const original = btn.innerHTML;
        btn.innerHTML = '✓ Denúncia Copiada! Escolha o Órgão Abaixo';
        btn.className = 'min-h-10 px-4 py-2 bg-[#00853b] text-white font-bold rounded-lg text-xs transition-all shadow-xs whitespace-nowrap';
        setTimeout(() => {
          btn.innerHTML = original;
          btn.className = 'min-h-10 px-4 py-2 bg-[#dc2626] hover:bg-[#b91c1c] text-white font-bold rounded-lg text-xs transition-all shadow-xs whitespace-nowrap';
        }, 3000);
      }
    });
  } else {
    const area = document.getElementById('textareaPeticaoLegal');
    if (area) {
      area.select();
      document.execCommand('copy');
    }
  }
}

// Expõe funções globais para manipulação de eventos inline
window.abrirModalRastreabilidade = abrirModalRastreabilidade;
window.navegarParaAba = navegarParaAba;
window.copiarPeticaoAtual = copiarPeticaoAtual;
