"""
Leitura das tabelas nativas do Freqtrade no PostgreSQL.
Somente SELECT — nunca escreve nas tabelas do Freqtrade.

Schema real do Freqtrade (sem bot_name — usamos 'strategy' como identificador).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from typing import Optional

from services.db import engine
from auth import require_key

router = APIRouter(prefix="/api/trades", tags=["trades"], dependencies=[Depends(require_key)])


def _run(sql: str, params: dict = None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        cols = result.keys()
        return [dict(zip(cols, row)) for row in result.fetchall()]


@router.get("")
def list_trades(
    strategy: Optional[str] = Query(None),
    pair: Optional[str] = Query(None),
    is_open: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
):
    """Trades com filtros. Lê das tabelas nativas do Freqtrade."""
    filters = ["1=1"]
    params: dict = {"limit": limit}

    if strategy:
        filters.append("strategy = :strategy")
        params["strategy"] = strategy
    if pair:
        filters.append("pair = :pair")
        params["pair"] = pair
    if is_open is not None:
        filters.append("is_open = :is_open")
        params["is_open"] = is_open

    where = " AND ".join(filters)
    sql = f"""
        SELECT id, strategy, pair, is_open, is_short,
               open_rate, close_rate, stake_amount,
               close_profit, close_profit_abs, realized_profit,
               open_date, close_date,
               exit_reason, leverage
        FROM trades
        WHERE {where}
        ORDER BY open_date DESC
        LIMIT :limit
    """
    return _run(sql, params)


@router.get("/performance")
def get_performance(strategy: Optional[str] = Query(None)):
    """P&L consolidado por estratégia (bots fechados)."""
    params = {}
    extra_filter = ""
    if strategy:
        extra_filter = "AND strategy = :strategy"
        params["strategy"] = strategy

    sql = f"""
        SELECT
            strategy,
            COUNT(*)                                              AS total_trades,
            SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END)    AS wins,
            SUM(CASE WHEN close_profit <= 0 THEN 1 ELSE 0 END)   AS losses,
            ROUND(AVG(close_profit)::numeric, 4)                  AS avg_profit_ratio,
            ROUND(SUM(close_profit_abs)::numeric, 4)              AS total_profit_usdt,
            ROUND(
                100.0 * SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            )                                                     AS win_rate_pct,
            ROUND(
                AVG(EXTRACT(EPOCH FROM (close_date - open_date)) / 3600.0)::numeric, 2
            )                                                     AS avg_duration_hours
        FROM trades
        WHERE is_open = false {extra_filter}
        GROUP BY strategy
        ORDER BY total_profit_usdt DESC
    """
    return _run(sql, params)


@router.get("/open")
def get_open_trades(strategy: Optional[str] = Query(None)):
    """Posições abertas agora."""
    params = {}
    extra_filter = ""
    if strategy:
        extra_filter = "AND strategy = :strategy"
        params["strategy"] = strategy

    sql = f"""
        SELECT id, strategy, pair, is_short,
               open_rate, stake_amount, leverage,
               open_date, realized_profit
        FROM trades
        WHERE is_open = true {extra_filter}
        ORDER BY open_date DESC
    """
    return _run(sql, params)
