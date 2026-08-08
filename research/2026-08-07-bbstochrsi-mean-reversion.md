# BBStochRSIMeanReversion — Pesquisa e Backtest

**Data:** 2026-08-07  
**Período testado:** 2025-01-02 → 2026-08-01 (575 dias)  
**Setup:** Binance Futures, $20 USDT  
**Status:** ❌ Descartada — a lógica de mean reversion não sobrevive ao bear market 2025

---

## Origem e lógica

**Fontes:**
- Base: [PeetCrypto/freqtrade-stuff — BB_RSI](https://github.com/PeetCrypto/freqtrade-stuff/blob/main/BB_RSI.py)
- Referência: [FMZ Multi-Factor Mean Reversion](https://www.fmz.com/lang/en/strategy/489893)
- Insight ADX: BB mean reversion profit factor 1.62 (ADX<20) vs -0.74 (trending)

**Lógica:** Opera em mercado lateral (ADX < 20). Entra long na banda inferior com StochRSI oversold, short na banda superior com overbought. Saída na banda média.

---

## Resultados — v1 vs v2

| Versão | Timeframe | Stop | Alavancagem | Lucro | Sharpe | Drawdown |
|---|---|---|---|---|---|---|
| v1 | 1h | -4% | 3x | -65% | -1.88 | 65% |
| v2 | 4h | -8% | 2x | **-57%** | -1.30 | 63% |

Os ajustes melhoraram marginalmente mas não resolveram o problema central.

---

## Diagnóstico final

**A lógica está certa, o mercado está errado para ela.**

O período testado (jan/2025 - ago/2026) foi um bear market com -42% de queda acumulada. Mean reversion em bear market tem um problema estrutural: o preço toca a banda inferior, a estratégia entra long esperando reversão, mas o mercado continua caindo — não é range, é tendência de baixa lenta.

O filtro ADX < 20 deveria resolver isso, mas em queda gradual o ADX fica baixo enquanto o preço escorrega continuamente. O indicador não distingue "lateral" de "queda lenta".

**Solução real:** adicionar um filtro de regime de mercado mais robusto — por exemplo, só entrar long se o preço estiver acima da SMA 200. Isso evita entradas long em downtrend disfarçado de lateral.

---

## Decisão

❌ **Descartada por agora.**

Guardar a ideia para quando o mercado mudar de regime (alta ou lateral real). A lógica é válida em condições diferentes.

---

## Tabela geral atualizada

| Estratégia | Lucro | Sharpe | Drawdown | Status |
|---|---|---|---|---|
| **FSupertrendStrategy** | **+94%** | **1.23** | 41% | ✅ Dry run ativo |
| FAdxSmaStrategy v2 | -33% | -0.72 | 38% | 🔄 Próximo ajuste |
| BBStochRSIMeanReversion v2 | -57% | -1.30 | 63% | ❌ Descartada |
| TrendFollowingStrategy | -66% | -0.51 | 67% | ❌ Descartada |
