from sqlalchemy import (
    create_engine, Column, String, Text, Integer,
    DateTime, Boolean, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from contextlib import contextmanager
from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# â”€â”€ Models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class Strategy(Base):
    __tablename__ = "hub_strategies"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), unique=True, nullable=False)
    code        = Column(Text, nullable=False)
    version     = Column(Integer, default=1, nullable=False)
    status      = Column(String(20), default="candidate")   # active | candidate | stopped
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Bot(Base):
    __tablename__ = "hub_bots"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String(100), unique=True, nullable=False)
    strategy_name   = Column(String(100), nullable=False)
    container_name  = Column(String(150))
    status          = Column(String(20), default="stopped")  # running | stopped | error
    dry_run         = Column(Boolean, default=True)
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BotConfig(Base):
    __tablename__ = "hub_bot_configs"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    bot_name          = Column(String(100), unique=True, nullable=False)
    encrypted_config  = Column(Text, nullable=False)
    updated_at        = Column(DateTime, server_default=func.now(), onupdate=func.now())


def create_tables():
    Base.metadata.create_all(bind=engine)


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

