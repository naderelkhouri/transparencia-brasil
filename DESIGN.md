---
name: Transparência Brasil
description: Sistema Sóbrio de Transparência Pública, Rigor Fiscal e Radar Anti-Corrupção
colors:
  primary: "#00853b"
  primary-hover: "#006b2f"
  primary-surface: "#ecfdf5"
  secondary: "#002776"
  secondary-surface: "#eff6ff"
  accent-amber: "#b45309"
  accent-amber-surface: "#fffbeb"
  tertiary: "#0284c7"
  corruption: "#dc2626"
  corruption-hover: "#b91c1c"
  corruption-surface: "#fef2f2"
  neutral-bg: "#ffffff"
  neutral-canvas: "#f8fafc"
  neutral-surface: "#ffffff"
  neutral-border: "#e2e8f0"
  neutral-border-strong: "#cbd5e1"
  neutral-text: "#0f172a"
  neutral-muted: "#475569"
  neutral-soft: "#64748b"
typography:
  display:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 4vw, 2.25rem)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.015em"
  title:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.05em"
  body:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "'JetBrains Mono', monospace"
    fontSize: "0.6875rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.025em"
rounded:
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  button-corruption:
    backgroundColor: "{colors.corruption}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  card-neutral:
    backgroundColor: "{colors.neutral-surface}"
    textColor: "{colors.neutral-text}"
    rounded: "{rounded.lg}"
    padding: "20px"
  card-corruption:
    backgroundColor: "{colors.corruption-surface}"
    textColor: "{colors.neutral-text}"
    rounded: "{rounded.lg}"
    padding: "20px"
---

# Design System: Transparência Brasil

## Overview

**Creative North Star: "O Livro Aberto da República"**

A linguagem visual da Transparência Brasil adota uma estética editorial sóbria, luminosa e rigorosa, assentada em fundo branco puro (`#ffffff`) e tela neutra em papel cívico (`#f8fafc`). A paleta homenageia a tradição republicana brasileira com contensão impecável: o Azul Institucional (`#002776`) confere autoridade e estrutura, o Verde Bandeira (`#00853b`) sinaliza execução orçamentária regular e quitação, e os acentos em Âmbar Ouro (`#b45309`, `#f59e0b`) pontuam fases preliminares como empenhos com contraste superior a 4.5:1.

O princípio central do sistema permanece inabalável: **o Vermelho Carmesim (`#dc2626`, `#ef4444`) é de uso estrito e exclusivo para o Radar Anti-Corrupção**. No fundo branco e calmo, o surgimento do vermelho funciona como um holofote ético sobre indícios de fraude, desvio e empresas sancionadas no CEIS.

**Key Characteristics:**
- **Sobriedade Luminosa:** Fundo claro com bordas de precisão de 1px e zero ruído decorativo.
- **Leitura Impecável:** Alto contraste tipográfico (Slate-900 `#0f172a` e Slate-700 `#334155` sobre branco puro).
- **Rigor Tabular:** Numerais monoespaçados com alinhamento tabular vertical em todas as métricas fiscais.
- **Reserva do Vermelho:** Vermelho exclusivamente semântico para corrupção e auditoria forense.

## Colors

A paleta combina a sobriedade do papel branco com as cores institucionais do Brasil e a cor de alerta crítico.

### Primary
- **Verde Bandeira Oficial** (`#00853b`): Execução orçamentária regular, pagamentos atestados e ações de pesquisa.
- **Verde Hover** (`#006b2f`): Estado ativo de foco e interação em botões primários.
- **Verde Superfície** (`#ecfdf5`): Tint sutil de fundo para badges e indicadores confirmatórios.

### Secondary
- **Azul Institucional** (`#002776`): Brasão nacional, cabeçalhos de tabela e identificador de autoridade da República.
- **Azul Superfície** (`#eff6ff`): Fundo suave de chips e filtros governamentais.

### Tertiary & Fiscal
- **Âmbar Ouro Legível** (`#b45309`): Fase de Empenho (NE) e destaques secundários com contraste garantido sobre branco.
- **Azul Celeste Técnico** (`#0284c7`): Repasses intergovernamentais fundo a fundo (SUS/FPM) e Liquidações.

### Corruption Alert (Exclusivo)
- **Vermelho Alerta** (`#dc2626`): Borda de denúncias, badges de empresas inidôneas e botões de auditoria.
- **Vermelho Superfície** (`#fef2f2`): Fundo claro carmesim de linhas e cartões sob suspeita no Radar de Corrupção.
- **Vermelho Texto Forte** (`#991b1b`): Texto de alta visibilidade e peso para descrições de desvios.

### Neutral
- **Branco Puro** (`#ffffff`): Fundo de cartões, tabelas e janelas de diálogo.
- **Papel Neutro Canvas** (`#f8fafc`): Fundo geral da página.
- **Cinza Delimitador** (`#e2e8f0`): Bordas e divisórias sutis de 1px.
- **Texto Principal** (`#0f172a`): Títulos e valores em destaque (contraste > 14:1).
- **Texto Secundário** (`#334155`): Textos de apoio e rótulos descritivos (contraste > 7:1).
- **Texto de Apoio** (`#475569`): Metadados, notas de rodapé e códigos orçamentários (contraste > 6.8:1 contra branco).

### Named Rules
**The Red Exclusivity Rule.** A cor vermelha é estritamente proibida em qualquer elemento que não seja uma ocorrência ou ferramenta do Radar Anti-Corrupção. Botões de fechar, status neutros e campos comuns utilizam cinzas ou azuis.

**The Contrast Floor Rule.** Nenhum texto de apoio pode ter taxa de contraste inferior a 4.5:1 contra a superfície branca ou cinza de fundo.

## Typography

**Display Font:** Public Sans (com fallback em `system-ui, -apple-system, sans-serif`)
**Body Font:** Public Sans (com fallback em `-apple-system, BlinkMacSystemFont, sans-serif`)
**Label & Numeric Font:** JetBrains Mono (com fallback em `ui-monospace, monospace`)

### Hierarchy
- **Display** (800, clamp(1.75rem, 4vw, 2.25rem), 1.15, -0.025em): Título principal e cabeçalho hero.
- **Headline** (700, 1.25rem, 1.3, -0.015em): Cabeçalhos de cartões, abas e diálogos de auditoria.
- **Title** (700, 0.875rem, 1.4, 0.05em): Títulos de tabelas e grupos analíticos.
- **Body** (400/500, 0.875rem, 1.5, normal): Descrições explicativas, notas técnicas e glossário com largura limitada a 70ch.
- **Label / Tabular** (600, 0.6875rem, 1.4, 0.025em): Números de notas de empenho, ordens bancárias, percentuais e valores monetários.

### Named Rules
**The Tabular Numerals Rule.** Todo valor numérico, moeda (R$), data e código orçamentário utiliza obrigatoriamente a propriedade `font-variant-numeric: tabular-nums` e a família `JetBrains Mono`.

## Layout

O layout baseia-se em um modelo de bancada analítica fluida e limpa (*full-width clean workbench*), que aproveita a largura total do monitor sem margens vazias desnecessárias, com padding horizontal responsivo de `1rem` (mobile) a `2.5rem` (desktops amplos: `w-full px-4 sm:px-6 lg:px-8 xl:px-10`).
- **Rhythm & Whitespace:** Espaçamentos verticais de `1.5rem` (24px) entre seções, conferindo leveza e clareza visual sem sobrecarga.
- **Tabelas de Dados em Largura Total:** As tabelas de despesas, municípios e credores ocupam 100% da largura útil, permitindo visualização confortável de todas as colunas sem estrangulamento de dados.
- **Alinhamento Numérico:** Colunas com valores monetários e quantidades são alinhadas à direita com numerais tabulares (`tabular-nums`), enquanto identificadores e textos descritivos são alinhados à esquerda.

## Elevation & Depth

O sistema adota uma abordagem de profundidade contida e estrutural baseada em bordas nítidas de 1px (`#e2e8f0`) e sombras suaves com difusão leve (`rgba(0, 0, 0, 0.04)`).

### Shadow Vocabulary
- **Sombra Suave Superfície** (`box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)`): Aplicada em cartões de métricas e tabelas.
- **Sombra de Alerta Anti-Corrupção** (`box-shadow: 0 4px 16px -2px rgba(220, 38, 38, 0.12)`): Aplicada exclusivamente em cartões sob suspeita no Radar de Corrupção.

### Named Rules
**The Single Elevation Rule.** Cartões declaram elevação através de uma borda nítida de 1px (`#e2e8f0`) e sombra sutil, sem acumular contornos pesados.

## Shapes

- **Cantos Arredondados:** 12px para contêineres e cartões principais; 8px para botões, inputs e pequenos cards; pílulas completas (`9999px`) exclusivamente para chips de status e badges.
- **Proibição de Bordas Laterais Espessas:** Nenhuma linha de tabela ou cartão utiliza borda lateral superior a 1px.

## Components

### Buttons
- **Shape:** Borda de raio 8px.
- **Primary (Verde Bandeira):** Fundo `#00853b`, texto `#ffffff`, hover `#006b2f`.
- **Corruption Audit (Vermelho):** Fundo `#dc2626`, texto `#ffffff`, hover `#b91c1c`.
- **Secondary / Ghost:** Fundo `#ffffff`, borda 1px `#e2e8f0`, texto `#334155`, hover `#f8fafc`.

### Badges de Fases Orçamentárias
- **Empenho:** Fundo `#fffbeb`, texto `#b45309`, borda 1px `#fde68a`.
- **Liquidação:** Fundo `#eff6ff`, texto `#1d4ed8`, borda 1px `#bfdbfe`.
- **Pagamento:** Fundo `#ecfdf5`, texto `#065f46`, borda 1px `#a7f3d0`.
- **Restos a Pagar:** Fundo `#fefce8`, texto `#854d0e`, borda 1px `#fef08a`.
- **Repasse:** Fundo `#f0f9ff`, texto `#0369a1`, borda 1px `#bae6fd`.
- **Corrupção / Alerta:** Fundo `#fef2f2`, texto `#991b1b`, borda 1px `#fca5a5`, ícone vetorial de alerta.

### Browser Surfaces
- **Text Selection:** `::selection { background: #00853b; color: #ffffff; }`.
- **Scrollbar:** Trilho em `#f8fafc`, barra de rolagem em `#cbd5e1`, hover em `#00853b`.
- **Focus Rings:** `:focus-visible { outline: 2px solid #002776; outline-offset: 2px; }`.

## Do's and Don'ts

### Do:
- **Do** manter o fundo branco e papel claro (`#ffffff`, `#f8fafc`) sóbrio e arejado.
- **Do** manter o Vermelho restrito 100% dos casos a situações de desvio, irregularidade grave e combate à corrupção.
- **Do** utilizar numerais tabulares (`tabular-nums`) e `JetBrains Mono` em todos os valores monetários e códigos fiscais.
- **Do** manter contraste mínimo de 4.5:1 para qualquer texto informativo.

### Don't:
- **Don't** utilizar emojis como ícones de interface.
- **Don't** aplicar `border-left: 4px` em linhas da tabela ou cartões.
- **Don't** utilizar textos com gradiente de cor.
- **Don't** utilizar texto amarelo claro sobre fundo branco (usar Âmbar `#b45309`).
