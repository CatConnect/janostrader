from sqlalchemy import (
    create_engine, Column, String, Text, Integer,
    DateTime, Boolean, func, text
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from contextlib import contextmanager
from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Strategy(Base):
    __tablename__ = "hub_strategies"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), unique=True, nullable=False)
    code       = Column(Text, nullable=False)
    version    = Column(Integer, default=1, nullable=False)
    status     = Column(String(20), default="candidate")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Bot(Base):
    __tablename__ = "hub_bots"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(100), unique=True, nullable=False)
    strategy_name  = Column(String(100), nullable=False)
    container_name = Column(String(150))
    dry_run        = Column(Boolean, default=True)
    timeframe      = Column(String(10), default="1h")
    last_seen      = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BotConfig(Base):
    __tablename__ = "hub_bot_configs"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    bot_name         = Column(String(100), unique=True, nullable=False)
    encrypted_config = Column(Text, nullable=False)
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())


def create_tables():
    Base.metadata.create_all(bind=engine)
    migrations = [
        "ALTER TABLE hub_bots ADD COLUMN IF NOT EXISTS timeframe VARCHAR(10) DEFAULT '1h'",
        "ALTER TABLE hub_bots ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP",
    ]
    with engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()


@contextmanager
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
