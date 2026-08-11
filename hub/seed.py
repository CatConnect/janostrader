"""
Registra (ou atualiza) um bot no hub.

Uso:
    python seed.py <bot_name> <strategy_name> [--live]

Exemplos:
    python seed.py supertrend FSupertrendStrategy
    python seed.py dualmacd  FDualMacdStrategy
    python seed.py supertrend FSupertrendStrategy --live   # desliga dry_run

Variáveis de ambiente necessárias (lidas do .env ou do ambiente do container):
    DATABASE_URL, ENCRYPTION_KEY, ACCESS_KEY
    BINANCE_API_KEY, BINANCE_API_SECRET
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID  (obrigatórios mesmo sem telegram ativo)
"""
import os
import sys

from config import settings  # garante que .env é carregado
from services.db import create_tables, get_db, Bot, BotConfig
from services.crypto import encrypt

# ── pares de configurações por bot ───────────────────────────────────────────

BOT_CONFIGS = {
    "supertrend": {
        "strategy_name": "FSupertrendStrategy",
        "container_name": "freqtrade-supertrend",
        "telegram_enabled": True,
        "api_server_port": 8080,
    },
    "dualmacd": {
        "strategy_name": "FDualMacdStrategy",
        "container_name": "freqtrade-dualmacd",
        "telegram_enabled": False,
        "api_server_port": 8081,
    },
}

# ── config base do Freqtrade ──────────────────────────────────────────────────

def build_config(bot_name: str, dry_run: bool) -> dict:
    meta = BOT_CONFIGS[bot_name]
    port = meta["api_server_port"]

    telegram_cfg: dict = {
        "enabled": meta["telegram_enabled"],
        "token": os.environ["TELEGRAM_BOT_TOKEN"],
        "chat_id": os.environ["TELEGRAM_CHAT_ID"],
    }
    if meta["telegram_enabled"]:
        telegram_cfg["notification_settings"] = {
            "status": "on", "warning": "on", "startup": "on",
            "entry": "on", "entry_fill": "on", "exit": "on",
            "exit_fill": "on", "exit_cancel": "on",
            "protection_trigger": "on", "protection_trigger_global": "on",
        }

    return {
        "$schema": "https://schema.freqtrade.io/schema.json",
        "max_open_trades": 3,
        "stake_currency": "USDT",
        "stake_amount": 7,
        "tradable_balance_ratio": 0.99,
        "fiat_display_currency": "USD",
        "dry_run": dry_run,
        "dry_run_wallet": 200,
        "trading_mode": "futures",
        "margin_mode": "isolated",
        "cancel_open_orders_on_exit": False,
        "unfilledtimeout": {
            "entry": 10, "exit": 10,
            "exit_timeout_count": 0, "unit": "minutes",
        },
        "entry_pricing": {
            "price_side": "same", "use_order_book": True,
            "order_book_top": 1, "price_last_balance": 0.0,
            "check_depth_of_market": {"enabled": False, "bids_to_ask_delta": 1},
        },
        "exit_pricing": {
            "price_side": "same", "use_order_book": True, "order_book_top": 1,
        },
        "exchange": {
            "name": "binance",
            "key": os.environ["BINANCE_API_KEY"],
            "secret": os.environ["BINANCE_API_SECRET"],
            "ccxt_config": {}, "ccxt_async_config": {},
            "pair_whitelist": [
                "BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT",
                "BNB/USDT:USDT", "XRP/USDT:USDT",
            ],
            "pair_blacklist": [],
        },
        "pairlists": [{"method": "StaticPairList"}],
        "telegram": telegram_cfg,
        "api_server": {
            "enabled": False,
            "listen_ip_address": "127.0.0.1",
            "listen_port": port,
            "username": "freqtrade",
            "password": "freqtrade",
            "jwt_secret_key": "somethingRandomSomethingRandom123",
        },
        "db_url": os.environ["DATABASE_URL"],
        "bot_name": bot_name,
        "initial_state": "running",
        "force_entry_enable": False,
        "internals": {"process_throttle_secs": 5},
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    live = "--live" in args
    args = [a for a in args if not a.startswith("--")]

    if not args:
        print("Uso: python seed.py <bot_name> [--live]")
        print("Bots disponíveis:", list(BOT_CONFIGS.keys()))
        sys.exit(1)

    bot_name = args[0]
    if bot_name not in BOT_CONFIGS:
        print(f"❌ Bot '{bot_name}' não reconhecido. Disponíveis: {list(BOT_CONFIGS.keys())}")
        sys.exit(1)

    dry_run = not live
    meta = BOT_CONFIGS[bot_name]
    strategy_name = meta["strategy_name"]

    create_tables()

    config = build_config(bot_name, dry_run=dry_run)

    with get_db() as db:
        bot = db.query(Bot).filter_by(name=bot_name).first()
        if not bot:
            db.add(Bot(
                name=bot_name,
                strategy_name=strategy_name,
                container_name=meta["container_name"],
                dry_run=dry_run,
            ))
            print(f"✅ Bot '{bot_name}' registrado (dry_run={dry_run})")
        else:
            bot.dry_run = dry_run
            print(f"ℹ️  Bot '{bot_name}' já existe — dry_run atualizado para {dry_run}")

        existing = db.query(BotConfig).filter_by(bot_name=bot_name).first()
        if not existing:
            db.add(BotConfig(bot_name=bot_name, encrypted_config=encrypt(config)))
            print(f"✅ Config '{bot_name}' encriptada e salva")
        else:
            existing.encrypted_config = encrypt(config)
            print(f"✅ Config '{bot_name}' atualizada")

    print(f"✅ Seed '{bot_name}' concluído (dry_run={dry_run})")


if __name__ == "__main__":
    main()
