from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from services.db import create_tables
from services.strategies import seed_from_files, sync_all_to_volume
from config import settings
from routers import internal, bots, strategies, trades


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Boot: cria tabelas, seed estratégias, sincroniza volume
    try:
        create_tables()
        print("✅ Tabelas criadas/verificadas no PostgreSQL")
    except Exception as e:
        print(f"⚠️  Erro ao criar tabelas (continuando): {e}")

    try:
        seed_path = Path(settings.STRATEGIES_SEED_PATH)
        seeded = 0
        for subdir in ["active", "candidates"]:
            seeded += seed_from_files(seed_path / subdir)
        if seeded:
            print(f"✅ {seeded} estratégia(s) importada(s) do repo para o PostgreSQL")
    except Exception as e:
        print(f"⚠️  Erro ao seed estratégias (continuando): {e}")

    try:
        synced = sync_all_to_volume()
        print(f"✅ {synced} estratégia(s) sincronizada(s) para o volume compartilhado")
    except Exception as e:
        print(f"⚠️  Erro ao sincronizar volume (continuando): {e}")

    yield


app = FastAPI(
    title="janostrader hub",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# Routers
app.include_router(internal.router)
app.include_router(bots.router)
app.include_router(strategies.router)
app.include_router(trades.router)

# Dashboard estÃ¡tico
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def dashboard():
        return FileResponse(str(static_dir / "index.html"))

