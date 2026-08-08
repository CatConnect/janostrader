from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from services.db import get_db, Strategy
from services.strategies import write_to_volume
from auth import require_key

router = APIRouter(prefix="/api/strategies", tags=["strategies"], dependencies=[Depends(require_key)])


class StrategyCreate(BaseModel):
    name: str
    code: str
    status: str = "candidate"


class StrategyUpdate(BaseModel):
    code: Optional[str] = None
    status: Optional[str] = None


@router.get("")
def list_strategies():
    with get_db() as db:
        strategies = db.query(Strategy).all()
        return [
            {
                "name": s.name,
                "version": s.version,
                "status": s.status,
                "updated_at": s.updated_at,
            }
            for s in strategies
        ]


@router.get("/{name}")
def get_strategy(name: str):
    with get_db() as db:
        s = db.query(Strategy).filter_by(name=name).first()
        if not s:
            raise HTTPException(404, f"EstratÃ©gia '{name}' nÃ£o encontrada")
        return {"name": s.name, "code": s.code, "version": s.version, "status": s.status}


@router.post("", status_code=201)
def create_strategy(data: StrategyCreate):
    with get_db() as db:
        existing = db.query(Strategy).filter_by(name=data.name).first()
        if existing:
            raise HTTPException(409, f"EstratÃ©gia '{data.name}' jÃ¡ existe")
        s = Strategy(name=data.name, code=data.code, status=data.status)
        db.add(s)
        write_to_volume(data.name, data.code)
    return {"created": data.name}


@router.put("/{name}")
def update_strategy(name: str, data: StrategyUpdate):
    with get_db() as db:
        s = db.query(Strategy).filter_by(name=name).first()
        if not s:
            raise HTTPException(404, f"EstratÃ©gia '{name}' nÃ£o encontrada")

        if data.code is not None:
            write_to_volume(name, data.code)   # valida sintaxe antes de salvar
            s.code = data.code
            s.version += 1

        if data.status is not None:
            valid = {"active", "candidate", "stopped"}
            if data.status not in valid:
                raise HTTPException(400, f"Status invÃ¡lido. Use: {valid}")
            s.status = data.status

    return {"updated": name, "version": s.version}

