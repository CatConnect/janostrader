“””
Endpoints internos — chamados pelo entrypoint do Freqtrade no boot.
Não expostos publicamente (requerem INTERNAL_KEY via header).
“””
from fastapi import APIRouter, HTTPException, Header
from typing import Annotated

from services.db import get_db, BotConfig
from services.crypto import decrypt
from config import settings

router = APIRouter(prefix=”/internal”, tags=[“internal”])


def _require_internal(x_internal_key: Annotated[str | None, Header()] = None):
    if x_internal_key != settings.INTERNAL_KEY:
        raise HTTPException(status_code=403, detail=”Forbidden”)


@router.get(“/config/{bot_name}”)
def get_bot_config(
    bot_name: str,
    x_internal_key: Annotated[str | None, Header()] = None,
):
    “””
    Retorna a config JSON decriptada para o bot.
    Chamado pelo entrypoint.sh de cada container Freqtrade no boot.
    Requer header X-Internal-Key.
    “””
    _require_internal(x_internal_key)
    with get_db() as db:
        cfg = db.query(BotConfig).filter_by(bot_name=bot_name).first()
        if not cfg:
            raise HTTPException(
                status_code=404,
                detail=f”Config não encontrada para o bot '{bot_name}'. “
                       “Registre o bot primeiro via hub.”
            )
        return decrypt(cfg.encrypted_config)


@router.get(“/health”)
def health():
    return {“status”: “ok”}

