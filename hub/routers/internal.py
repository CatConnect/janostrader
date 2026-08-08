"""
Endpoints internos â€” chamados pelo entrypoint do Freqtrade no boot.
NÃ£o expostos publicamente.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path

from services.db import get_db, BotConfig, Bot
from services.crypto import decrypt

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/config/{bot_name}")
def get_bot_config(bot_name: str):
    """
    Retorna a config JSON decriptada para o bot.
    Chamado pelo entrypoint.sh de cada container Freqtrade no boot.
    """
    with get_db() as db:
        cfg = db.query(BotConfig).filter_by(bot_name=bot_name).first()
        if not cfg:
            raise HTTPException(
                status_code=404,
                detail=f"Config nÃ£o encontrada para o bot '{bot_name}'. "
                       "Registre o bot primeiro via hub."
            )
        return decrypt(cfg.encrypted_config)


@router.get("/health")
def health():
    return {"status": "ok"}

