"""
Gerencia estratÃ©gias: PostgreSQL como fonte de verdade,
volume compartilhado como destino para o Freqtrade ler.
"""
import os
import py_compile
import tempfile
from pathlib import Path

from config import settings
from services.db import get_db, Strategy


STRATEGIES_VOLUME = Path(settings.STRATEGIES_VOLUME_PATH)


def write_to_volume(name: str, code: str) -> None:
    """Valida sintaxe e escreve o .py no volume compartilhado."""
    # Valida sintaxe antes de escrever
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        py_compile.compile(tmp_path, doraise=True)
    finally:
        os.unlink(tmp_path)

    # Escreve no volume
    STRATEGIES_VOLUME.mkdir(parents=True, exist_ok=True)
    dest = STRATEGIES_VOLUME / f"{name}.py"
    dest.write_text(code, encoding="utf-8")


def sync_all_to_volume() -> int:
    """Escreve todas as estratÃ©gias ativas/candidatas no volume. Retorna quantidade."""
    count = 0
    with get_db() as db:
        strategies = db.query(Strategy).filter(
            Strategy.status.in_(["active", "candidate"])
        ).all()
        for s in strategies:
            write_to_volume(s.name, s.code)
            count += 1
    return count


def seed_from_files(strategies_dir: Path) -> int:
    """
    Seed inicial: lÃª .py do repo e insere no PostgreSQL se nÃ£o existir.
    Chamado uma vez no boot do hub.
    """
    count = 0
    if not strategies_dir.exists():
        return 0

    with get_db() as db:
        for py_file in strategies_dir.glob("*.py"):
            name = py_file.stem
            if name.startswith("__"):
                continue
            existing = db.query(Strategy).filter_by(name=name).first()
            if not existing:
                code = py_file.read_text(encoding="utf-8")
                # Determina status pelo diretÃ³rio pai
                parent = py_file.parent.name
                status = "active" if parent == "active" else "candidate"
                db.add(Strategy(name=name, code=code, status=status))
                count += 1
    return count

