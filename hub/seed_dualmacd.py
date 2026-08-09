"""
Registra o bot dualmacd no hub (FDualMacdStrategy, dry run, sem Telegram).
Execute uma vez após o hub estar rodando.
"""
import os
from config import settings
from services.db import create_tables, get_db, Bot, BotConfig
from services.crypto import encrypt

BOT_NAME      = "dualmacd"
STRATEGY_NAME = "FDualMacdStrategy"

config = {
    "$schema": "https://schema.freqtrade.io/schema.json",
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": 7,
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "dry_run": True,
    "dry_run_wallet": 200,
    "trading_mode": "futures",
    "margin_mode": "isolated",
    "cancel_open_orders_on_exit": False,
    "unfilledtimeout": {"entry": 10, "exit": 10, "exit_timeout_count": 0, "unit": "minutes"},
    "entry_pricing": {
        "price_side": "same", "use_order_book": True,
        "order_book_top": 1, "price_last_balance": 0.0,
        "check_depth_of_market": {"enabled": False, "bids_to_ask_delta": 1}
    },
    "exit_pricing": {"price_side": "same", "use_order_book": True, "order_book_top": 1},
    "exchange": {
        "name": "binance",
        "key": os.environ["BINANCE_API_KEY"],
        "secret": os.environ["BINANCE_API_SECRET"],
        "ccxt_config": {}, "ccxt_async_config": {},
        "pair_whitelist": ["BTC/USDT:USDT","ETH/USDT:USDT","SOL/USDT:USDT","BNB/USDT:USDT","XRP/USDT:USDT"],
        "pair_blacklist": []
    },
    "pairlists": [{"method": "StaticPairList"}],
    "telegram": {"enabled": False},
    "api_server": {"enabled": False},
    "db_url": os.environ["DATABASE_URL"],
    "bot_name": BOT_NAME,
    "initial_state": "running",
    "force_entry_enable": False,
    "internals": {"process_throttle_secs": 5}
}

create_tables()

with get_db() as db:
    if not db.query(Bot).filter_by(name=BOT_NAME).first():
        db.add(Bot(name=BOT_NAME, strategy_name=STRATEGY_NAME,
                   container_name="freqtrade-dualmacd", dry_run=True))
        print(f"✅ Bot '{BOT_NAME}' registrado")
    else:
        print(f"ℹ️  Bot '{BOT_NAME}' já existe")

    existing = db.query(BotConfig).filter_by(bot_name=BOT_NAME).first()
    if not existing:
        db.add(BotConfig(bot_name=BOT_NAME, encrypted_config=encrypt(config)))
        print(f"✅ Config '{BOT_NAME}' encriptada e salva")
    else:
        existing.encrypted_config = encrypt(config)
        print(f"✅ Config '{BOT_NAME}' atualizada")

print("✅ Seed dualmacd concluído")
