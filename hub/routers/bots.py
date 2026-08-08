from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from services.db import get_db, Bot, BotConfig, Strategy
from services.crypto import encrypt, decrypt
from auth import require_key

router = APIRouter(prefix="/api/bots", tags=["bots"], dependencies=[Depends(require_key)])


class BotCreate(BaseModel):
    name: str
    strategy_name: str
    dry_run: bool = True
    binance_api_key: str
    binance_api_secret: str
    telegram_token: str
    telegram_chat_id: str
    db_url: str
    extra_config: Optional[dict] = None


class BotUpdate(BaseModel):
    strategy_name: Optional[str] = None
    dry_run: Optional[bool] = None


def _build_config(bot: "BotCreate | dict", bot_name: str) -> dict:
    """Monta o config.json completo do Freqtrade."""
    if isinstance(bot, dict):
        bk = bot["binance_api_key"]
        bs = bot["binance_api_secret"]
        tt = bot["telegram_token"]
        tc = bot["telegram_chat_id"]
        db_url = bot["db_url"]
        dry_run = bot.get("dry_run", True)
        extra = bot.get("extra_config") or {}
    else:
        bk = bot.binance_api_key
        bs = bot.binance_api_secret
        tt = bot.telegram_token
        tc = bot.telegram_chat_id
        db_url = bot.db_url
        dry_run = bot.dry_run
        extra = bot.extra_config or {}

    base = {
        "$schema": "https://schema.freqtrade.io/schema.json",
        "max_open_trades": 3,
        "stake_currency": "USDT",
        "stake_amount": 7,
        "tradable_balance_ratio": 0.99,
        "fiat_display_currency": "USD",
        "dry_run": dry_run,
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
            "key": bk,
            "secret": bs,
            "ccxt_config": {},
            "ccxt_async_config": {},
            "pair_whitelist": ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT", "XRP/USDT:USDT"],
            "pair_blacklist": []
        },
        "pairlists": [{"method": "StaticPairList"}],
        "telegram": {
            "enabled": True,
            "token": tt,
            "chat_id": tc,
            "notification_settings": {
                "status": "on", "warning": "on", "startup": "on",
                "entry": "on", "entry_fill": "on", "exit": "on",
                "exit_fill": "on", "exit_cancel": "on",
                "protection_trigger": "on", "protection_trigger_global": "on"
            }
        },
        "api_server": {
            "enabled": True,
            "listen_ip_address": "0.0.0.0",
            "listen_port": 8080,
            "verbosity": "error",
            "jwt_secret_key": "janostrader2026secretkey_xK9mP3qL7nR2vT8wA5cE1hJ4bN6yU0s",
            "CORS_origins": [],
            "username": "janostrader",
            "password": "janos2026"
        },
        "db_url": db_url,
        "bot_name": bot_name,
        "initial_state": "running",
        "force_entry_enable": False,
        "internals": {"process_throttle_secs": 5}
    }
    base.update(extra)
    return base


@router.get("")
def list_bots():
    with get_db() as db:
        bots = db.query(Bot).all()
        return [
            {
                "name": b.name,
                "strategy": b.strategy_name,
                "status": b.status,
                "dry_run": b.dry_run,
                "container": b.container_name,
                "created_at": b.created_at,
            }
            for b in bots
        ]


@router.post("", status_code=201)
def create_bot(data: BotCreate):
    with get_db() as db:
        # Verifica se estratÃ©gia existe
        strat = db.query(Strategy).filter_by(name=data.strategy_name).first()
        if not strat:
            raise HTTPException(404, f"EstratÃ©gia '{data.strategy_name}' nÃ£o encontrada")

        existing = db.query(Bot).filter_by(name=data.name).first()
        if existing:
            raise HTTPException(409, f"Bot '{data.name}' jÃ¡ existe")

        # Cria bot
        bot = Bot(name=data.name, strategy_name=data.strategy_name, dry_run=data.dry_run)
        db.add(bot)

        # Encripta e salva config
        config = _build_config(data, data.name)
        cfg = BotConfig(bot_name=data.name, encrypted_config=encrypt(config))
        db.add(cfg)

    return {"created": data.name}


@router.get("/{name}/config")
def get_bot_config_preview(name: str):
    """Retorna config sem secrets (para preview no dashboard)."""
    with get_db() as db:
        cfg = db.query(BotConfig).filter_by(bot_name=name).first()
        if not cfg:
            raise HTTPException(404, "Config nÃ£o encontrada")
        config = decrypt(cfg.encrypted_config)
        # Remove secrets antes de retornar
        config.get("exchange", {}).pop("key", None)
        config.get("exchange", {}).pop("secret", None)
        config.get("telegram", {}).pop("token", None)
        return config


@router.delete("/{name}", status_code=204)
def delete_bot(name: str):
    with get_db() as db:
        bot = db.query(Bot).filter_by(name=name).first()
        if not bot:
            raise HTTPException(404, "Bot nÃ£o encontrado")
        db.query(BotConfig).filter_by(bot_name=name).delete()
        db.delete(bot)

