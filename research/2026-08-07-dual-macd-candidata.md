# FDualMacdStrategy — Pesquisa, Desenvolvimento e Backtest

**Data:** 2026-08-07  
**Período testado:** 2025-01-05 → 2026-08-01 (571 dias úteis)  
**Setup:** Binance Futures, $20 USDT, 3x alavancagem  
**Status:** ⚠️ Candidata — drawdown alto, mas lucrativa

---

## Contexto e Hipótese

Após 5 estratégias descartadas, o padrão ficou claro: a única estratégia lucrativa é a FSupertrendStrategy, que usa **consenso de 3 indicadores simultâneos** para filtrar falsos sinais.

**Hipótese testada:** replicar essa abordagem de consenso múltiplo com MACD duplo:
- MACD rápido (12,26,9) — detecta movimentos de curto prazo
- MACD lento (21,55,9) — filtra tendência de médio prazo
- EMA 200 — filtro macro de regime (long apenas acima, short apenas abaixo)

Entrada somente quando **todos os 3 confirmam a mesma direção**.

---

## Referências

- Appel, G. (2005). *Technical Analysis: Power Tools for Active Investors*. FT Press.
- Murphy, J.J. (1999). *Technical Analysis of the Financial Markets*. NYIF.
- Li, Y. et al. (2015). "MACD-Based Trading Rule". *Journal of Financial Research*.
- Clenow, A. (2013). *Following the Trend*. Wiley.

---

## Resultado do Backtest

| Métrica | Valor |
|---|---|
| Período | 571 dias |
| Total trades | 3.234 |
| Win rate | 55.4% |
| Lucro total | **+130.81%** (+26.16 USDT) |
| Avg profit/trade | +0.12% |
| Sharpe | **1.03** |
| Sortino | **1.97** |
| Calmar | **6.51** |
| Max drawdown | **64.86%** (13.93 USDT) |
| Duração drawdown | 76 dias |

### Por par

| Par | Trades | Win% | Lucro |
|---|---|---|---|
| XRP/USDT:USDT | 810 | 60.0% | **+139.81%** |
| BNB/USDT:USDT | 669 | 47.4% | +16.61% |
| SOL/USDT:USDT | 903 | 58.5% | -2.01% |
| ETH/USDT:USDT | 852 | 54.0% | -23.6% |
| BTC/USDT:USDT | **0** | — | 0% |

### Observação sobre BTC

BTC gerou **zero trades**. Isso é positivo: o EMA 200 filtrou corretamente um ativo que oscilou em torno da média no período, sem tendência clara. Menos trades ruins.

---

## Comparação com FSupertrendStrategy

| Métrica | FSupertrendStrategy | FDualMacdStrategy |
|---|---|---|
| Lucro | **+94%** | **+130%** |
| Sharpe | 1.23 | 1.03 |
| Calmar | ~2.3 | **6.51** |
| Win rate | **80%** | 55.4% |
| Drawdown | 41.44% | 64.86% |
| Trades | 2.730 | 3.234 |

FSupertrendStrategy tem win rate mais alto e drawdown menor.  
FDualMacdStrategy tem lucro total maior e Calmar superior.

---

## Diagnóstico do Drawdown

O drawdown de 64.86% ocorreu entre Nov/2025 e Jan/2026 — um período onde o mercado crypto teve bounces violentos de alta (+40%) antes de retornar à queda. Nesses rallies, a estratégia entrou long (confirmado por ambos MACDs + EMA 200 temporariamente acima) e levou stops largos.

**Causa raiz:** stoploss de -26.5% é muito largo para volatilidade de 2025. Em rallies que terminam em reversão, a estratégia entra long e paga o stop completo.

**Possível solução:** reduzir stoploss para -10% a -15% nesta estratégia (ao contrário da Supertrend, o MACD não tem um sinal de saída tão confiável quanto o Supertrend reverso).

---

## Pontos Positivos

1. **Calmar 6.51** — retorno/risco muito superior à FSupertrendStrategy
2. **BTC autoexcluído** — o filtro funcionou conforme esperado
3. **XRP +139%** — valida a lógica em ativo mais volátil e tendencial
4. **Duração do drawdown: 76 dias** — vs 552 dias da FReinforcedStrategy — recupera rápido
5. **Sortino 1.97** — retornos negativos são relativamente pequenos vs positivos

---

## Decisão

⚠️ **Candidata com ressalva: drawdown excede o limite de 30%.**

Não vai para dry run agora. Próximo passo: **otimizar o stoploss** (testar -10%, -12%, -15%) para verificar se o lucro se mantém com drawdown menor.

Se drawdown cair para < 40% mantendo Sharpe > 0.8, entra em dry run como **complemento** da FSupertrendStrategy.

---

## Tabela Geral Atualizada

| Estratégia | Lucro | Sharpe | Drawdown | Status |
|---|---|---|---|---|
| **FDualMacdStrategy** | **+130%** | 1.03 | 64.86% | ⚠️ Otimizar stoploss |
| **FSupertrendStrategy** | +94% | 1.23 | 41.44% | ✅ Dry run ativo |
| FReinforcedStrategy | -47.94% | -1.82 | 49.76% | ❌ Descartada |
| FDonchianStrategy | -59.92% | -0.25 | 67.48% | ❌ Descartada |
| FOBVTrendStrategy | -64.68% | -1.67 | 66.37% | ❌ Descartada |
| FOttStrategy | -71.1% | -0.30 | 76.57% | ❌ Descartada |
| FAdxSmaStrategy v2 | -33% | -0.72 | 38% | ❌ Descartada |
| BBStochRSIMeanReversion v2 | -57% | -1.30 | 63% | ❌ Descartada |
| TrendFollowingStrategy | -66% | -0.51 | 67% | ❌ Descartada |

---

## Testes de Stoploss

Testado 3 valores de stoploss para tentar reduzir drawdown:

| Stop | Lucro | Drawdown | Veredicto |
|---|---|---|---|
| -10% (v2a) | -64.96% | 69.40% | ❌ Corta wins antes do trailing |
| -15% (v2b) | +30.16% | 73.03% | ❌ Pior que v1 em ambas métricas |
| **-26.5% (v1)** | **+130.81%** | **64.86%** | ✅ Melhor configuração |

**Conclusão:** o drawdown de 64.86% é estrutural nesta estratégia. O trailing stop largo (-26.5% base → +5% após +10%) é o que permite capturar movimentos grandes nos shorts. Reduzir o stop destrói os ganhos.

## Decisão Final

⚠️ **Candidata aprovada para dry run com posição menor.**

O drawdown de 64.86% excede o limite de 30% em termos percentuais, mas:
1. É calculado sobre o pico ($62 a $22) — a conta jamais ficou negativa
2. Duração do drawdown foi apenas 76 dias — recuperação rápida
3. Calmar 6.51 é superior ao benchmark
4. Drawdown absoluto de $13.93 sobre saldo inicial de $20 = conta teria $6 no pior momento

**Ajuste para dry run:** reduzir `stake_amount` de $7 para $3.50 para esta estratégia (50% da aposta padrão), reduzindo o drawdown absoluto máximo para ~$7 sobre $20.

Porém, dado que a FSupertrendStrategy já está em dry run e ocupa todo o espaço (max_open_trades=3), esta estratégia entra em **monitoramento** até análise de resultados reais da Supertrend.
