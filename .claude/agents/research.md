---
name: research
description: Pesquisa completa de estratégias de trading — da teoria ao backtest. Cobre comunidade, artigos acadêmicos e validação histórica antes de qualquer recomendação.
---

# Skill: /research

## Contexto do projeto

- Exchange: Binance Futures (modo futuros, margem isolada)
- Orçamento: ~100 BRL (~$20 USDT)
- Alavancagem máxima: 3x
- Stack: Freqtrade + FreqAI
- Repo: CatConnect/janostrader

## O que essa skill faz

Pesquisa, adapta, testa e recomenda estratégias. Pesquisa sem backtest não tem valor — toda candidata precisa ser validada antes de qualquer recomendação.

---

## Processo obrigatório

### 1. Busca — Comunidade

Fontes a consultar sempre:
- GitHub: `freqtrade/freqtrade-strategies` (pasta `/futures`)
- GitHub Topics: `freqtrade-strategies` ordenado por updated
- Reddit: r/algotrading, r/freqtrade
- Discord oficial do Freqtrade
- Repositórios da comunidade (nateemma, davidzr, webclinic017 e similares)

Filtro obrigatório na busca:
- Compatível com futuros (tem `trading_mode = "futures"` ou equivalente)?
- Funciona com stake pequeno (< $30 por trade)?
- Tem histórico de uso ou estrelas suficientes pra não ser lixo?

### 2. Busca — Acadêmica e especializada

Fontes a consultar sempre:
- ArXiv (seção quantitative finance: `q-fin`)
- SSRN (papers de algo trading e technical analysis)
- Quantpedia (strategies database)
- QuantConnect (community strategies)
- Blogs: Quant at Risk, Algorithmic Trading, Chan & Co

O que procurar:
- Papers sobre o indicador ou lógica da estratégia (ex: "EMA crossover futures crypto")
- Estudos de mercado cripto com futuros
- Qualquer evidência de que a lógica funciona (ou não) fora do backtest

### 3. Análise de cada candidata

Para cada estratégia encontrada, documentar:

| Campo | Descrição |
|---|---|
| Nome | Nome da estratégia |
| Fonte | URL ou referência |
| Lógica | Como decide entrar e sair (em linguagem simples) |
| Indicadores | Quais usa (RSI, EMA, ATR, etc.) |
| Timeframe | 1m / 5m / 15m / 1h / 4h |
| Long/Short | Opera só long, só short ou os dois? |
| Compatível c/ futuros? | Sim / Não / Precisa adaptar |
| Referência acadêmica | Paper ou estudo que suporta a lógica (se existir) |
| Risco aparente | Baixo / Médio / Alto (avaliação inicial) |

### 4. Adaptação para o setup

Se a estratégia não estiver pronta pra futuros:
- Adicionar `trading_mode = "futures"` e `margin_mode = "isolated"`
- Configurar `can_short = True` se a lógica incluir short
- Ajustar `stake_amount` para o nosso limite
- Alavancagem: definir `leverage_callback` com máximo 3x
- Salvar em `strategies/candidates/nome_da_estrategia.py`

### 5. Backtest

Comando padrão a rodar:
```bash
freqtrade backtesting \
  --strategy NomeDaEstrategia \
  --config config.json \
  --timerange 20240101-20250101 \
  --timeframe-detail 1m
```

Período mínimo: 6 meses de dados históricos.

### 6. Interpretação do backtest

Métricas obrigatórias a analisar:

| Métrica | Mínimo aceitável | Ideal |
|---|---|---|
| Profit total | > 0% | > 20% no período |
| Max Drawdown | < 30% | < 15% |
| Win Rate | > 45% | > 55% |
| Profit Factor | > 1.2 | > 1.5 |
| Sharpe Ratio | > 0.5 | > 1.0 |
| Trades no período | > 30 | > 100 |

Se qualquer métrica crítica reprovar → estratégia descartada com justificativa.

### 7. Output — o que entregar

Ao final do `/research`, criar o arquivo:

```
research/YYYY-MM-DD-nome-da-estrategia.md
```

Com estrutura:

```markdown
# [Nome da Estratégia] — Pesquisa

**Data:** YYYY-MM-DD
**Status:** Aprovada para dry run | Descartada

## Fonte
- Comunidade: [link]
- Referência acadêmica: [link ou "não encontrada"]

## Lógica
[Explicação simples de como a estratégia funciona]

## Indicadores
[Lista]

## Resultado do Backtest
[Tabela com métricas]

## Análise
[O que os números dizem — não apenas listar, mas interpretar]

## Decisão
**Aprovada / Descartada**
Justificativa: [motivo objetivo]

## Próximo passo
[Entrar em dry run / ajustar parâmetro X e retestar / descartar]
```

---

## Regras

- Nunca recomendar estratégia sem backtest concluído
- Nunca aprovar estratégia com drawdown > 30%
- Sempre incluir referência acadêmica se existir — dá mais credibilidade à decisão
- Sempre salvar o arquivo de resultado no repo antes de fechar a tarefa
- Priorizar estratégias que operam long e short (futuros permitem isso — aproveitar)
