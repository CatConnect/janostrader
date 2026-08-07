# Pesquisa Inicial de Estratégias — Futuros Binance

**Data:** 2026-08-07  
**Contexto:** Binance Futures, ~$20 USDT, alavancagem máx 3x, Freqtrade  
**Fontes consultadas:** freqtrade/freqtrade-strategies (oficial), freqst.com, arXiv, Medium

---

## Candidatas encontradas

### 1. FSupertrendStrategy ⭐ Recomendada para testar primeiro

**Fonte:** [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/futures/FSupertrendStrategy.py)  
**Referência acadêmica:** Supertrend é amplamente documentado em literatura de análise técnica quantitativa. O paper ["Systematic Trend-Following with Adaptive Portfolio Construction"](https://arxiv.org/html/2602.11708v1) valida a lógica de trend-following em crypto com Sharpe 2.41 e drawdown máximo de 12.7%.

**Como funciona:**  
Usa 6 indicadores Supertrend simultâneos (3 pra entrada, 3 pra saída). Só entra quando TODOS os 3 do lado concordam — filtro de consenso forte que reduz sinais falsos. Confirma com volume.

| Campo | Valor |
|---|---|
| Indicadores | 6x Supertrend (ATR-based) + Volume |
| Timeframe | 1h |
| Long + Short | ✅ |
| Stop Loss | -26.5% (trailing) |
| ROI alvo | 2.5% → 5% → 7.5% → 10% |
| Startup candles | 18 |
| Compatível c/ futuros | ✅ nativo |

**Pontos positivos:**
- Lógica de consenso (3 de 3) reduz muito entrada em ruído
- Trailing stop protege ganhos
- Opera long e short — aproveita os dois lados do mercado
- Parâmetros otimizáveis via hyperopt

**Pontos de atenção:**
- Stop de -26.5% é largo — com 3x alavancagem representa risco real
- Timeframe 1h = menos trades por dia (paciência necessária)
- Precisa ajustar leverage_callback para máx 3x

**Decisão:** ✅ **Aprovada para backtest**

---

### 2. TrendFollowingStrategy ⭐ Segunda a testar

**Fonte:** [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/futures/TrendFollowingStrategy.py)  
**Referência acadêmica:** ["Follow the Leader: Enhancing Systematic Trend-Following Using Network Momentum"](https://arxiv.org/html/2501.07135v1) — valida combinação de momentum de preço + volume para trend-following.

**Como funciona:**  
EMA 20 como baseline de tendência + OBV (volume acumulado) como confirmação de momentum. Entra quando preço cruza a EMA E o volume confirma a direção. Simples e eficiente.

| Campo | Valor |
|---|---|
| Indicadores | EMA 20 + OBV |
| Timeframe | 5m |
| Long + Short | ✅ |
| Stop Loss | -26.5% (trailing) |
| ROI alvo | 5% → 10% → 15% |
| Compatível c/ futuros | ✅ nativo |

**Pontos positivos:**
- Timeframe 5m = muito mais trades, dados acumulam mais rápido
- Lógica simples = fácil de entender por que entrou e saiu
- Volume como filtro evita entradas em movimentos falsos

**Pontos de atenção:**
- 5m pode gerar overtrading em mercado lateral
- Mais trades = mais taxas (importante com conta pequena)
- Stop de -26.5% idem ao anterior — precisa ajuste

**Decisão:** ✅ **Aprovada para backtest**

---

### 3. FAdxSmaStrategy — Terceira

**Fonte:** [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/futures/FAdxSmaStrategy.py)

**Como funciona:**  
ADX mede a força da tendência (não a direção). Só entra quando a tendência é forte o suficiente (ADX > 30) E o cruzamento de SMAs (12/48) confirma a direção. Sai quando a tendência enfraquece (ADX cai).

| Campo | Valor |
|---|---|
| Indicadores | ADX 14 + SMA 12 + SMA 48 |
| Timeframe | 1h |
| Long + Short | ✅ |
| Stop Loss | -5% (fixo) |
| ROI alvo | 5% → 10% → 7.5% |
| Compatível c/ futuros | ✅ nativo |

**Pontos positivos:**
- Stop de -5% é o mais adequado para conta pequena com alavancagem
- ADX filtra mercado lateral — só opera em tendência real
- Lógica clássica, muito documentada

**Pontos de atenção:**
- Cruzamento de SMA é lento — pode entrar tarde na tendência
- ADX como saída pode segurar posição perdedora por muito tempo

**Decisão:** ✅ **Aprovada para backtest**

---

### 4. VolatilitySystem — Descartada por agora

**Fonte:** [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/futures/VolatilitySystem.py)

**Problema:** Stop loss configurado como -1 (praticamente sem stop). Com conta de $20 e alavancagem, isso é inaceitável. A lógica de resampling para 3 minutos também adiciona complexidade desnecessária neste momento.

**Decisão:** ❌ **Descartada — sem stop loss adequado para conta pequena**

---

## Insight acadêmico relevante

O paper [Systematic Trend-Following with Adaptive Portfolio Construction](https://arxiv.org/html/2602.11708v1) testou 150+ pares cripto em 36 meses (2022-2024) e chegou a:
- Sharpe Ratio: **2.41**
- Drawdown máximo: **-12.7%**
- Retorno anualizado: **40.5%**
- Timeframe ótimo: **6h** (H1 e H4 geram taxas demais, H12+ perde sinais curtos)

**O que isso nos diz:** trend-following funciona em cripto. A lógica das nossas candidatas é válida. O timeframe de 1h é conservador mas razoável.

---

## Próximos passos

### Ordem de backtest

| Prioridade | Estratégia | Motivo |
|---|---|---|
| 1ª | FSupertrendStrategy | Lógica mais robusta, consenso de 3 indicadores |
| 2ª | FAdxSmaStrategy | Stop fixo de -5% é o mais seguro pra conta pequena |
| 3ª | TrendFollowingStrategy | Mais trades = mais dados, testar em paralelo |

### Comandos de backtest a rodar

```bash
# Baixar dados históricos (6 meses)
freqtrade download-data \
  --exchange binance \
  --trading-mode futures \
  --timeframe 1h 5m \
  --timerange 20250101-20260101 \
  --pairs BTC/USDT:USDT ETH/USDT:USDT SOL/USDT:USDT BNB/USDT:USDT XRP/USDT:USDT

# Backtest FSupertrendStrategy
freqtrade backtesting \
  --strategy FSupertrendStrategy \
  --config config.json \
  --timerange 20250101-20260101

# Backtest FAdxSmaStrategy
freqtrade backtesting \
  --strategy FAdxSmaStrategy \
  --config config.json \
  --timerange 20250101-20260101

# Backtest TrendFollowingStrategy
freqtrade backtesting \
  --strategy TrendFollowingStrategy \
  --config config.json \
  --timerange 20250101-20260101 \
  --timeframe 5m
```

### Métricas mínimas para aprovação para dry run

| Métrica | Mínimo |
|---|---|
| Lucro total | > 0% |
| Drawdown máximo | < 30% |
| Win Rate | > 45% |
| Profit Factor | > 1.2 |
| Sharpe Ratio | > 0.5 |
| Total de trades | > 30 |

---

## Ajustes obrigatórios antes do backtest

Todas as estratégias precisam dos seguintes ajustes no código para o nosso setup:

```python
# Alavancagem máxima 3x
def leverage(self, pair, current_time, current_rate, proposed_leverage,
             max_leverage, entry_tag, side):
    return 3.0

# Modo futuros
trading_mode = TradingMode.FUTURES
margin_mode = MarginMode.ISOLATED
```
