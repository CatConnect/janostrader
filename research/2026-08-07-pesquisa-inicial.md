# Pesquisa Inicial de Estratégias — Futuros Binance

**Data:** 2026-08-07  
**Período testado:** 2025-01-01 → 2026-08-01 (576 dias)  
**Setup:** Binance Futures, $20 USDT, 3x alavancagem, 5 pares (BTC/ETH/SOL/BNB/XRP)  
**Status:** ✅ Concluída

---

## Resultado dos Backtests

| Estratégia | Lucro Total | Profit Factor | Sharpe | Drawdown | Win Rate | Trades | Decisão |
|---|---|---|---|---|---|---|---|
| **FSupertrendStrategy** | **+94.09%** | **1.04** | **1.23** | 41.44% | 80.0% | 2730 | ✅ **DRY RUN** |
| FAdxSmaStrategy | -17.26% | 0.75 | -0.38 | 19.23% | 35.8% | 95 | ❌ Ajustar |
| TrendFollowingStrategy | -65.80% | 0.70 | -0.51 | 66.92% | 76.8% | 112 | ❌ Descartar |

---

## Análise Detalhada

### 🏆 FSupertrendStrategy — APROVADA

**Resultado:** $20 → $38.82 USDT em 576 dias (+94%)  
**Contexto de mercado:** Período bear (-42% no mercado). A estratégia lucrou **contra a maré**.

**O que funcionou:**
- Short side foi o motor: **+103.34%** de lucro no lado short
- Long side ficou ligeiramente negativo (-9.25%) — esperado em bear market
- Win rate de 80% com 2730 trades = consistência estatística sólida
- 2182 trades saíram por ROI (100% de acerto nesses) — a estratégia sabe quando sair com lucro

**Pontos de atenção:**
- Drawdown de 41.44% é alto — entre fev/2026 e mai/2026 a carteira caiu de $63 para $17
- Profit factor 1.04 é baixo — a margem entre ganhos e perdas é fina
- Exit signal com 0% de win rate: quando a estratégia decide sair por sinal, está sempre errada — isso é um ponto claro de melhoria
- BTC não operou nenhum trade — pares com pouca volatilidade ficam travados

**Conclusão:** Funciona. Com mercado lateralizando ou caindo, o short side segura. Precisa de ajuste no exit_signal para não destruir ganhos. Entra em dry run.

---

### ⚠️ FAdxSmaStrategy — AJUSTAR ANTES DE RETESTAR

**Resultado:** $20 → $16.55 USDT (-17.26%)  
**O que o ADX está fazendo:** entrando em 95 trades, mas atingindo stop loss em 31 deles (33%). O cruzamento de SMA está atrasado — entra depois que o movimento já aconteceu.

**Diagnóstico claro:**
- Quando sai por ROI: 21 trades, 100% win, +45.84% — a lógica tem valor
- Quando sai por exit_signal: 43 trades, 30% win — o sinal de saída está errado
- Quando bate stop: 31 trades, 0% win, -55.32% — o stop de -5% correto mas acontece cedo demais

**O que ajustar:**
1. Reduzir `sma_long_period` de 48 para 20-30 — entrada mais rápida
2. Aumentar `pos_entry_adx` de 30 para 35 — entrar só em tendências mais fortes
3. Revisar lógica de exit_signal — está saindo cedo demais nos winners

**Decisão:** Não entra em dry run agora. Retestar após ajustes nos parâmetros.

---

### ❌ TrendFollowingStrategy — DESCARTADA

**Resultado:** $20 → $6.84 USDT (-65.80%). Drawdown de 66.92% em 61 dias corridos logo no início.

**Causa raiz:** O trailing stop de -26.5% está destruindo a estratégia. Em 5m, um movimento brusco aciona o stop e a perda (-23.5% por trade quando trailing stop é acionado) anula todos os wins do ROI. A relação risco/retorno está invertida: ganha pequeno, perde grande.

**Decisão:** ❌ Descartada. Lógica EMA+OBV tem potencial mas precisa de stop completamente diferente para o timeframe 5m. Pode ser reavaliada no futuro com stop de -3% fixo.

---

## Próximos passos

### Imediato
1. **FSupertrendStrategy entra em dry run** — configurar bot para rodar com ela
2. **Monitorar por 7-14 dias** — ver se o comportamento real bate com o backtest
3. **Analisar exit_signal** — entender por que os 444 exits por sinal têm 0% de win

### Médio prazo
4. **Ajustar FAdxSmaStrategy** e retestar
5. **Buscar nova estratégia** com foco em proteção de capital no long side
6. **Primeira análise** (`/analyse`) após 50 trades no dry run

---

## Referências

- [freqtrade/freqtrade-strategies — pasta futures](https://github.com/freqtrade/freqtrade-strategies/tree/main/user_data/strategies/futures)
- [arXiv 2602.11708 — Systematic Trend-Following Crypto](https://arxiv.org/html/2602.11708v1): Sharpe 2.41, drawdown -12.7% em 150+ pares 2022-2024. Valida a lógica de trend-following.
- [arXiv 2501.07135 — Network Momentum](https://arxiv.org/html/2501.07135v1): valida volume como confirmador de momentum
