from fastapi import APIRouter, Depends

from services.db import get_db, Bot
from auth import require_key

router = APIRouter(prefix="/api/bots", tags=["bots"], dependencies=[Depends(require_key)])


@router.get("")
def list_bots():
    with get_db() as db:
        bots = db.query(Bot).all()
        return [
            {
                "name": b.name,
                "strategy": b.strategy_name,
                "dry_run": b.dry_run,
                "timeframe": b.timeframe or "1h",
                "container": b.container_name,
                "last_seen": b.last_seen.isoformat() if b.last_seen else None,
                "created_at": b.created_at,
            }
            for b in bots
        ]
