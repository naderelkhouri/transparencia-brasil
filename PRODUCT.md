# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Cidadãos Brasileiros e Contribuintes:** Desejam acompanhar onde o dinheiro dos seus impostos está sendo aplicado, em linguagem clara e visualmente acessível, sem jargões contábeis impenetráveis.
- **Jornalistas Investigativos e Pesquisadores:** Necessitam de dados confiáveis, cruzamento de fontes oficiais e rastreabilidade total (linagem, hash SHA-256 e link direto para o comprovante original).
- **Auditores Cívicos, ONGs e Conselhos Sociais:** Monitoram a aplicação de verbas municipais e federais (como FUNDEB e FNS), identificando discrepâncias fiscais, sobrepreço e empresas inidôneas.

## Product Purpose

A Transparência Brasil é uma plataforma analítica e de controle social que unifica os dados de despesas públicas dos três níveis federativos (Federal, Estadual e Municipal), fundamentada na Lei nº 4.320/1964, na Lei de Responsabilidade Fiscal (LC nº 101/2000) e na Lei de Acesso à Informação (Lei nº 12.527/2011).

O sistema resolve a fragmentação dos dados públicos brasileiros, impedindo a bitributação/dupla contagem em repasses intergovernamentais e fornecendo um **Radar Anti-Corrupção** automatizado que destaca indícios de irregularidades graves e empresas punidas no CEIS/CGU.

## Positioning

Diferente de dashboards genéricos que somam contratos, empenhos e liquidações como se fossem o mesmo dinheiro, a plataforma respeita o ciclo contábil da despesa pública brasileira (Dotação ➔ Empenho ➔ Liquidação ➔ Pagamento ➔ Restos a Pagar), isola transferências fundo a fundo para apurar o **Gasto Efetivo Real** e disponibiliza rastreabilidade pericial com contratos de proveniência auditáveis até o Portal da Transparência, SICONFI e PNCP.

## Operating Context

- **Fontes Oficiais Integradas:**
  - Portal da Transparência do Governo Federal (CGU / SIAFI).
  - SICONFI / Secretaria do Tesouro Nacional (relatórios contábeis e fiscais dos 5.570 municípios e 27 estados).
  - Portal Nacional de Contratações Públicas (PNCP, Lei nº 14.133/2021).
  - Cadastro de Empresas Inidôneas e Suspensas (CEIS / CGU).
- **Ambiente de Uso:** Navegadores modernos (Desktop e Mobile), visualização em tempo real de painéis orçamentários, exportação aberta em CSV e consulta por API REST.

## Capabilities and Constraints

- **Capacidades:**
  - Ingestão automatizada de despesas federais, contratos do PNCP e dados fiscais municipais do SICONFI.
  - Normalização e armazenamento analítico em colunas (Apache Parquet + DuckDB).
  - Isolamento formal de transferências intergovernamentais (`is_transferencia_intergovernamental = true`) para eliminar a dupla contagem.
  - Radar Anti-Corrupção com regras heurísticas de auditoria (empresas inidôneas no CEIS, indícios de sobrepreço atípico e fracionamento de licitação).
  - Rastreabilidade ponta-a-ponta com hash criptográfico SHA-256 de proveniência de cada registro ingerido.
  - Exportação direta de Dados Abertos (CSV) streaming.
- **Restrições:**
  - Respeito estrito aos limites de taxa e contratos de dados das APIs públicas.
  - Imutabilidade dos registros de extração brutos (camada Bronze/Raw).
  - Esquema estrito nas cores do Brasil (Verde Bandeira, Amarelo Ouro, Azul Noturno e Branco), com uso exclusivo da cor Vermelha para alertas de corrupção.

## Brand Commitments

- **Identidade Visual:** Brasil Institucional e Cívico — Verde Bandeira (`#009c3b`), Amarelo Ouro (`#ffdf00`), Azul Noturno Imperial (`#030a16`, `#08182f`), e Branco (`#ffffff`).
- **Regra Sagrada da Cor Vermelha:** O tom vermelho (`#ef4444`, `#dc2626`) é terminantemente reservado e exclusivo para alertar "Corrupção, Suspeita de Desvio e Irregularidades Graves". Nunca deve ser usado para decorações triviais, status comuns ou elementos neutros da interface.
- **Tipografia:** Plus Jakarta Sans para leitura e hierarquia; JetBrains Mono para valores monetários, números tabulares, códigos orçamentários, identificadores e hashes de auditoria.
- **Iconografia:** Ícones vetoriais SVG autorais e geométricos, de traço limpo e consistente. É vetado o uso de emojis comuns como sistema iconográfico.

## Evidence on Hand

- Amostras de dados reais do Portal da Transparência (CGU/SIAFI), SICONFI (Tesouro Nacional) e PNCP (Contratações Públicas) ingeridos e processados nas partições Parquet e DuckDB.
- Códigos de notas de empenho reais (e.g. `2026NE000412`, `2026NE000105`, `2026NE000882`) e cruzamento com o CEIS/CGU para empresas inidôneas demonstrando indícios reais de irregularidade.

## Product Principles

1. **Rigor da Lei 4.320/64:** Nunca misturar empenho, liquidação e pagamento. Cada fase contábil possui seu significado jurídico e financeiro próprio.
2. **Anti-Dupla Contagem:** Transferências federais para estados e municípios não são somadas duas vezes no Gasto Efetivo Nacional.
3. **Auditabilidade Incondicional:** Todo número exibido deve poder ser rastreado até o seu documento e fonte original com um clique.
4. **Voz Cívica e Imparcial:** Análise baseada em dados oficiais e critérios técnicos de auditoria do TCU/CGU, sem viés partidário.
5. **Destaque Máximo ao Combate à Corrupção:** A interface deve direcionar a atenção do cidadão para qualquer desvio do erário com clareza imediata e inequívoca.

## Accessibility & Inclusion

- Conformidade com as diretrizes WCAG 2.1 AA (contraste mínimo de 4.5:1 para textos corporais e 3:1 para elementos de destaque).
- Navegação completa por teclado com anéis de foco visíveis (`focus-visible`).
- Numerais com alinhamento tabular (`font-variant-numeric: tabular-nums`) para permitir comparação numérica precisa.
- Suporte a leitores de tela em tabelas e cards com atributos ARIA semânticos.
