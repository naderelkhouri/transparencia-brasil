---
name: Transparência Brasil
description: Sistema de Transparência Pública, Rigor Fiscal e Radar Anti-Corrupção
colors:
  primary: "#009c3b"
  primary-hover: "#00b343"
  secondary: "#ffdf00"
  secondary-amber: "#f59e0b"
  tertiary: "#38bdf8"
  corruption: "#ef4444"
  corruption-deep: "#dc2626"
  corruption-surface: "rgba(239, 68, 68, 0.12)"
  neutral-bg: "#030a16"
  neutral-surface: "#08162b"
  neutral-border: "#122b52"
  neutral-text: "#ffffff"
  neutral-muted: "#94a3b8"
  neutral-soft: "#cbd5e1"
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
  md: "10px"
  lg: "14px"
  xl: "18px"
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
    textColor: "{colors.neutral-text}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-corruption:
    backgroundColor: "{colors.corruption-deep}"
    textColor: "{colors.neutral-text}"
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

**Creative North Star: "O Escudo Cívico Republicano"**

A linguagem visual da Transparência Brasil une a sobriedade institucional da República à contundência de uma ferramenta de auditoria cívica de ponta. A paleta é orgulhosamente ancorada nas cores nacionais do Brasil: o Azul Noturno Imperial (`#030a16`, `#08162b`) atua como base sólida e solene, o Verde Bandeira (`#009c3b`) sinaliza execução orçamentária regular e legalidade, e o Amarelo Ouro (`#ffdf00`) guia a atenção do olhar para títulos e métricas de destaque.

O elemento definidor e inflexível do sistema é a reserva moral da cor Vermelha: **o Vermelho não é usado para decoração nem status comuns; ele pertence exclusivamente ao Radar Anti-Corrupção**. Quando o vermelho surge na tela, ele corta a paleta com intensidade máxima, sinalizando à sociedade indícios graves de desvio de verbas, empresas punidas pelo CEIS e sobrepreço.

**Key Characteristics:**
- **Solenidade Cívica:** Estética republicana, livre de clichês e ruído visual desnecessário.
- **Rigor Numérico:** Tipografia monoespaçada com numerais tabulares em todos os dados financeiros.
- **Iconografia Vetorial Autoral:** Ícones em SVG nítidos de 1.5px/2px de espessura de traço, abolindo emojis da interface.
- **Reserva do Vermelho:** Vermelho com sinalização semântica absoluta de corrupção.

## Colors

A paleta é dividida entre as cores cívicas nacionais e a cor crítica de combate à corrupção.

### Primary
- **Verde Bandeira** (`#009c3b`): Representa regularidade fiscal, pagamentos realizados com respaldo legal e ações confirmatórias.
- **Verde Esmeralda Hover** (`#00b343`): Feedback tátil em botões primários e estados ativos de regularidade.

### Secondary
- **Amarelo Ouro** (`#ffdf00`): Destaques hierárquicos, acentos de marca, avisos de restos a pagar e cabeçalhos de tabelas.
- **Amarelo Âmbar** (`#f59e0b`): Fase orçamentária de Empenho (reserva de dotação).

### Tertiary
- **Azul Celeste Técnico** (`#38bdf8`): Repasses intergovernamentais (Fundo a Fundo: SUS/FPM) e fase contábil de Liquidação.

### Corruption Alert (Exclusivo)
- **Vermelho Alerta** (`#ef4444`): Borda de cartões de denúncia, badges de empresas inidôneas e textos de alerta.
- **Vermelho Profundo** (`#dc2626`): Botões de auditoria forense e ações punitivas no Radar Anti-Corrupção.
- **Vermelho Superfície** (`rgba(239, 68, 68, 0.12)`): Fundo sutil de linhas e áreas sob suspeita contábil.

### Neutral
- **Azul Noturno Profundo** (`#030a16`): Fundo principal da aplicação (`background`).
- **Azul Card Superfície** (`#08162b`): Superfície de cartões analíticos e tabelas.
- **Azul Borda Contida** (`#122b52`): Delimitação sutil de blocos e divisórias (1px).
- **Branco Puro** (`#ffffff`): Texto de alto contraste e valores numéricos em destaque.
- **Azul Suave Muted** (`#cbd5e1` / `#94a3b8`): Texto secundário com contraste garantido ≥ 4.5:1.

### Named Rules
**The Red Exclusivity Rule.** A cor vermelha é estritamente proibida em qualquer elemento que não seja uma ocorrência ou ferramenta do Radar Anti-Corrupção. Botões de cancelar, erros de digitação comuns e status padrão utilizam tons neutros ou âmbar. O vermelho é guardado para manter seu peso de denúncia intacto.

**The Contrast Floor Rule.** Nenhum texto de apoio pode ter taxa de contraste inferior a 4.5:1 contra a superfície de fundo. Superfícies escuras utilizam texto em `#ffffff`, `#cbd5e1` ou `#94a3b8`, nunca cinzas apagados.

## Typography

**Display Font:** Public Sans (com fallback em `system-ui, sans-serif`)
**Body Font:** Public Sans (com fallback em `-apple-system, BlinkMacSystemFont, sans-serif`)
**Label & Numeric Font:** JetBrains Mono (com fallback em `ui-monospace, monospace`)

A tipografia combina uma fonte sem serifa contemporânea e límpida com uma fonte monoespaçada pericial para exibir identificadores contábeis, hashes SHA-256 e valores em Reais (BRL).

### Hierarchy
- **Display** (800, clamp(1.75rem, 4vw, 2.25rem), 1.15, -0.025em): Título principal e cabeçalho de grandes seções.
- **Headline** (700, 1.25rem, 1.3, -0.015em): Cabeçalhos de cartões, abas e diálogos de auditoria.
- **Title** (700, 0.875rem, 1.4, 0.05em): Títulos de tabelas, seções secundárias e cabeçalhos de grupos.
- **Body** (400/500, 0.8125rem, 1.5, normal): Descrições explicativas, notas técnicas e glossário com largura limitada a 70ch.
- **Label / Tabular** (600, 0.6875rem, 1.4, 0.025em): Números de notas de empenho, ordens bancárias, percentuais e valores monetários.

### Named Rules
**The Tabular Numerals Rule.** Todo valor numérico, moeda (R$), data e código orçamentário utiliza obrigatoriamente a propriedade `font-variant-numeric: tabular-nums` e a família `JetBrains Mono` para assegurar alinhamento vertical rigoroso nas tabelas.

## Layout

O layout baseia-se em um grid responsivo com container centralizado de largura máxima de `80rem` (1280px) com padding horizontal de `1rem` a `2rem`.
- **Rhythm:** Espaçamentos verticais de `1rem` (16px), `1.5rem` (24px) e `2rem` (32px).
- **Densidade:** Alta densidade de informação analítica, organizada em cartões com agrupamento lógico claro.
- **Tabelas com Rolagem Horizontal Segura:** Tabelas de dados granulares possuem container com `overflow-x: auto` e cabeçalhos sem quebra de linha.

## Elevation & Depth

O sistema adota uma abordagem de profundidade contida e estrutural baseada em bordas nítidas de 1px e iluminação sutil de superfície. Não são permitidas sombras duras sem desfoque (zero-blur block shadows) nem sobreposições de múltiplos contornos fantasmas.

### Shadow Vocabulary
- **Sombra Institucional Superfície** (`box-shadow: 0 4px 20px -2px rgba(3, 10, 22, 0.6)`): Aplicada em cartões de métricas e tabelas.
- **Sombra de Alerta Anti-Corrupção** (`box-shadow: 0 0 24px -4px rgba(239, 68, 68, 0.25)`): Aplicada exclusivamente em cartões sob suspeita no Radar de Corrupção.

### Named Rules
**The Single Elevation Rule.** Cartões e contêineres declaram sua elevação através de uma borda nítida de 1px (`#122b52`) ou de uma sombra suave difusa, nunca acumulando bordas espessas de múltiplas cores.

## Shapes

- **Cantos Arredondados:** 14px a 16px para contêineres e cartões principais; 8px a 10px para botões, inputs e pequenos cards; pílulas completas (`9999px`) exclusivamente para chips de status e badges.
- **Proibição de Bordas Laterais Espessas:** Nenhuma linha de tabela ou cartão utiliza borda lateral (`border-left` ou `border-right`) superior a 1px. Destaques são realizados com tint de fundo e badges dedicados.

## Components

### Buttons
- **Shape:** Borda de raio 8px (sm/md).
- **Primary (Verde Bandeira):** Fundo `#009c3b`, texto `#ffffff`, hover `#00b343`, foco visível com anel de 2px em `#ffdf00`.
- **Corruption Audit (Vermelho):** Fundo `#dc2626`, texto `#ffffff`, hover `#ef4444`, sombra de alerta.
- **Secondary / Ghost:** Fundo `#08162b`, borda 1px `#122b52`, texto `#cbd5e1`, hover `#122b52`.

### Badges de Fases Orçamentárias
- **Empenho:** Fundo `rgba(245, 158, 11, 0.15)`, texto `#fbbf24`, borda 1px `rgba(245, 158, 11, 0.4)`.
- **Liquidação:** Fundo `rgba(59, 130, 246, 0.15)`, texto `#60a5fa`, borda 1px `rgba(59, 130, 246, 0.4)`.
- **Pagamento:** Fundo `rgba(0, 156, 59, 0.15)`, texto `#34d399`, borda 1px `rgba(0, 156, 59, 0.4)`.
- **Restos a Pagar:** Fundo `rgba(217, 119, 6, 0.15)`, texto `#fde68a`, borda 1px `rgba(217, 119, 6, 0.4)`.
- **Repasse:** Fundo `rgba(14, 165, 233, 0.15)`, texto `#38bdf8`, borda 1px `rgba(14, 165, 233, 0.4)`.
- **Corrupção / Alerta:** Fundo `rgba(239, 68, 68, 0.2)`, texto `#fca5a5`, borda 1px `#ef4444`, ícone vetorial de alerta.

### Browser Surfaces
- **Text Selection:** `::selection { background: #009c3b; color: #ffffff; }`.
- **Scrollbar:** Trilho em `#030a16`, barra de rolagem em `#122b52`, hover em `#009c3b`.
- **Focus Rings:** `:focus-visible { outline: 2px solid #ffdf00; outline-offset: 2px; }`.

## Do's and Don'ts

### Do:
- **Do** manter o Vermelho restrito 100% dos casos a situações de desvio, irregularidade grave e combate à corrupção.
- **Do** utilizar numerais tabulares (`tabular-nums`) e `JetBrains Mono` em todos os valores monetários e códigos fiscais.
- **Do** utilizar ícones SVG desenhados com espessura homogênea (16x16 ou 20x20).
- **Do** manter contraste mínimo de 4.5:1 para qualquer texto informativo.
- **Do** respeitar as três fases formais da Lei nº 4.320/64 (Empenho, Liquidação, Pagamento) sem agrupá-las arbitrariamente.

### Don't:
- **Don't** utilizar emojis como ícones de interface (ex.: proibir 🏛️, 🇧🇷, 🚨, 📥, 🛡️, 🔍 como elementos de controle).
- **Don't** aplicar `border-left: 4px` em linhas da tabela ou cartões; utilizar badges e tint de fundo.
- **Don't** utilizar textos com gradiente de cor; usar hierarquia de peso e contraste.
- **Don't** misturar valores de transferências intergovernamentais com gastos diretos do governo para evitar bitributação.
- **Don't** utilizar sombras pretas duras sem difusão.
