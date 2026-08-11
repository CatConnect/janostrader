"""
Endpoints internos — chamados pelo entrypoint do Freqtrade no boot e em loop.
Requerem X-Internal-Key header.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Header
from typing import Annotated

from services.db import get_db, BotConfig, Bot
from services.crypto import decrypt
from config import settings

router = APIRouter(prefix="/internal", tags=["internal"])


def _require_internal(x_internal_key: Annotated[str | None, Header()] = None):
    if x_internal_key != settings.INTERNAL_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/config/{bot_name}")
def get_bot_config(
    bot_name: str,
    x_internal_key: Annotated[str | None, Header()] = None,
):
    """
    Retorna a config JSON decriptada para o bot.
    Chamado pelo entrypoint.sh no boot. Requer X-Internal-Key.
    """
    _require_internal(x_internal_key)
    with get_db() as db:
        cfg = db.query(BotConfig).filter_by(bot_name=bot_name).first()
        if not cfg:
            raise HTTPException(
                status_code=404,
                detail=f"Config não encontrada para o bot '{bot_name}'. "
                       "Registre o bot primeiro via hub."
            )
        # Atualiza last_seen no boot
        bot = db.query(Bot).filter_by(name=bot_name).first()
        if bot:
            bot.last_seen = datetime.now(timezone.utc)
        return decrypt(cfg.encrypted_config)


@router.post("/heartbeat/{bot_name}", status_code=204)
def heartbeat(
    bot_name: str,
    x_internal_key: Annotated[str | None, Header()] = None,
):
    """
    Atualiza last_seen do bot. Chamado pelo entrypoint.sh a cada 60s.
    Requer X-Internal-Key.
    """
    _require_internal(x_internal_key)
    with get_db() as db:
        bot = db.query(Bot).filter_by(name=bot_name).first()
        if not bot:
            raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' não encontrado")
        bot.last_seen = datetime.now(timezone.utc)


@router.get("/health")
def health():
    return {"status": "ok"}
