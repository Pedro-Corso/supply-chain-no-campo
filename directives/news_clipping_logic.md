# Directive: Lógica de Agregação de Notícias para Procurement

Esta diretiva define como o sistema de clipping deve processar e exibir informações para o departamento de Procurement.

## Objetivo
Garantir que as notícias exibidas sejam relevantes para a mitigação de riscos em suprimentos de máquinas agrícolas (pulverizadores e colhedoras).

## Entradas (Fontes de Dados)
- Feeds RSS de portais de notícias econômicas, agrícolas e industriais.
- APIs de notícias abertas (ex: Google News RSS).

## Processo de Filtragem e Categorização
1. **Categorização Temporal**:
   - Calcular a diferença entre a data atual e a data de publicação (`pubDate`).
   - Atribuir às categorias: `Últimas 24h`, `Últimos 7 dias`, `Últimos 30 dias`.

2. **Filtragem de Idioma**:
   - Oferecer toggle entre conteúdos em Português (Brasil) e Inglês (Global).

3. **Temas Pertinentes**:
   - **Cadeia de Suprimentos**: Logística, fretes, portos, transportes.
   - **Materiais**: Aço, borracha, plásticos de engenharia, resinas.
   - **Eletrônica**: Semicondutores, sensores, cablagens.
   - **Energia**: Preço do óleo diesel, impacto em custos logísticos.

## Saída Esperada
- Um dashboard em HTML moderno, visualmente atraente e responsivo.
- Cards de notícias contendo: Título, Fonte, Data, Categoria de Risco e Link Original.

## Tratamento de Erros
- Se um feed falhar, ignorar silenciosamente ou mostrar um aviso discreto para não quebrar a interface.
