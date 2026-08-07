---
name: analyse
description: Análise de resultados de estratégias em dry run ou live. Avalia performance, identifica padrões e decide: manter, ajustar ou desligar.
---

# Skill: /analyse

## Contexto do projeto

- Exchange: Binance Futures
- Orçamento: ~100 BRL (~$20 USDT)
- Stack: Freqtrade + FreqAI
- Banco de dados: SQLite (tradesv3.sqlite)
- Repo: CatConnect/janostrader

## O que essa skill faz

Analisa os dados reais de performance das estratégias rodando (dry run ou live). Toda análise termina com uma decisão clara: manter, ajustar ou desligar. Não existe análise sem decisão.

---

## Processo obrigatório

### 1. Coleta de dados

Fontes de dados a consultar:

**SQLite — trades:**
```sql
SELECT * FROM trades WHERE is_open = 0 ORDER BY close_date DESC;
```

**SQLite — ordens:**
```sql
SELECT * FROM orders WHERE status = 'closed' ORDER BY order_date DESC;
```

**Logs do Freqtrade:**
- `user_data/logs/freqtrade.log`

**Exports de performance:**
- `freqtrade trade-summary` ou via API REST do bot

Período mínimo de análise:
- Dry run: mínimo 7 dias ou 50 trades (o que vier primeiro)
- Live: mínimo 14 dias ou 30 trades

### 2. Métricas a calcular

**Performance geral:**

| Métrica | Como calcular | Referência |
|---|---|---|
| Lucro total (%) | soma dos profits_ratio | > 0 |
| Drawdown máximo | maior sequência de perdas | < 30% |
| Win Rate | trades positivos / total | > 45% |
| Profit Factor | soma ganhos / soma perdas | > 1.2 |
| Média por trade | lucro médio por operação | > 0.3% |
| Trades por dia | total / dias rodando | — |

**Performance por dimensão:**

- Por par (BTC/USDT, ETH/USDT, etc.) — quais estão dando lucro?
- Por horário (0h-6h, 6h-12h, 12h-18h, 18h-24h) — quando rende mais?
- Por direção (long vs short) — qual lado está performando?
- Por dia da semana — padrão de mercado

### 3. Identificação de padrões

Perguntas obrigatórias a responder:

1. Algum par está claramente destruindo a performance? (candidato a blacklist)
2. Tem horário com win rate abaixo de 35%? (candidato a filtrar)
3. O lado short está funcionando ou só perdendo? (rever se vale manter)
4. Os trades perdedores têm algo em comum? (horário, par, condição de mercado)
5. O stop loss está sendo atingido com frequência anormal? (stop muito curto?)
6. A estratégia performa diferente em mercado em tendência vs lateral?

### 4. Decisão

Cada estratégia em análise recebe uma de três decisões:

**MANTER** — métricas dentro do aceitável, continuar monitorando
- Documentar o que está funcionando bem

**AJUSTAR** — tem potencial mas algo está errado
- Especificar exatamente o que ajustar (parâmetro, par, horário, stop)
- Definir prazo para reanalisar após ajuste

**DESLIGAR** — não está funcionando, não vale continuar
- Justificar com dados (não opinião)
- Se foi live: calcular perda total e documentar lição aprendida

### 5. Output — o que entregar

Criar o arquivo:

```
analysis/YYYY-MM-DD-nome-da-estrategia.md
```

Com estrutura:

```markdown
# [Nome da Estratégia] — Análise de Performance

**Data:** YYYY-MM-DD
**Período analisado:** DD/MM até DD/MM
**Modo:** Dry Run | Live
**Decisão: MANTER | AJUSTAR | DESLIGAR**

---

## Números

| Métrica | Resultado | Status |
|---|---|---|
| Lucro total | X% | ✅ / ⚠️ / ❌ |
| Drawdown | X% | ✅ / ⚠️ / ❌ |
| Win Rate | X% | ✅ / ⚠️ / ❌ |
| Profit Factor | X.X | ✅ / ⚠️ / ❌ |
| Total de trades | N | — |

## O que está funcionando
[Pares, horários, condições que performam bem]

## O que está com problema
[Pares, horários, condições que estão puxando pra baixo]

## Decisão: [MANTER / AJUSTAR / DESLIGAR]

**Justificativa:**
[Baseado nos dados, não em opinião]

**Ação:**
[O que vai ser feito agora — blacklist de par X, ajuste de parâmetro Y, desligar, etc.]

**Próxima análise:**
[Data ou gatilho — ex: "em 7 dias" ou "quando atingir 50 trades"]
```

---

## Regras

- Toda análise termina com uma decisão — nunca "vamos ver mais um pouco" sem prazo definido
- Decisão de desligar é baseada em dados, não em impaciência ou medo
- Ajustes são específicos — nunca "vou melhorar a estratégia" sem dizer exatamente o quê
- Sempre salvar o arquivo no repo antes de fechar
- Se dois ciclos de ajuste consecutivos não melhorarem: desligar sem hesitar
- Pares com win rate < 35% por 14 dias → blacklist automática, sem discussão
