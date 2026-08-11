"""
Script de seed: registra o bot supertrend no hub.
Execute uma vez apÃ³s o hub estar rodando:
  docker exec janostrader-hub python -m hub.seed_bot
"""
import os, sys

# Garante que as env vars estÃ£o disponÃ­veis
from config import settings
from services.db import create_tables, get_db, Bot, BotConfig, Strategy
from services.crypto import encrypt

BOT_NAME       = "supertrend"
STRATEGY_NAME  = "FSupertrendStrategy"

config = {
    "$schema": "https://schema.freqtrade.io/schema.json",
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": 7,
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "dry_run": True,
    "dry_run_wallet": 20,
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
    "telegram": {
        "enabled": True,
        "token": os.environ["TELEGRAM_BOT_TOKEN"],
        "chat_id": os.environ["TELEGRAM_CHAT_ID"],
        "notification_settings": {
            "status": "on", "warning": "on", "startup": "on",
            "entry": "on", "entry_fill": "on", "exit": "on",
            "exit_fill": "on", "exit_cancel": "on",
            "protection_trigger": "on", "protection_trigger_global": "on"
        }
    },
    "api_server": {
        "enabled": False,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "username": "freqtrade",
        "password": "freqtrade",
        "jwt_secret_key": "somethingRandomSomethingRandom123"
    },
    "db_url": os.environ["DATABASE_URL"],
    "bot_name": BOT_NAME,
    "initial_state": "running",
    "force_entry_enable": False,
    "internals": {"process_throttle_secs": 5}
}

create_tables()

with get_db() as db:
    # Bot
    if not db.query(Bot).filter_by(name=BOT_NAME).first():
        db.add(Bot(name=BOT_NAME, strategy_name=STRATEGY_NAME,
                   container_name="freqtrade-supertrend", dry_run=True))
        print(f"âœ… Bot '{BOT_NAME}' registrado")
    else:
        print(f"â„¹ï¸  Bot '{BOT_NAME}' jÃ¡ existe")

    # Config encriptada
    existing_cfg = db.query(BotConfig).filter_by(bot_name=BOT_NAME).first()
    if not existing_cfg:
        db.add(BotConfig(bot_name=BOT_NAME, encrypted_config=encrypt(config)))
        print(f"âœ… Config do bot '{BOT_NAME}' encriptada e salva")
    else:
        existing_cfg.encrypted_config = encrypt(config)
        print(f"âœ… Config do bot '{BOT_NAME}' atualizada")

print("âœ… Seed concluÃ­do")

