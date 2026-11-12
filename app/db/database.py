"""Configuração da conexão e das sessões do banco."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import obter_configuracao


def _opcoes_do_engine(url: str) -> dict:
    if url.startswith("sqlite"):
        opcoes = {"connect_args": {"check_same_thread": False}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            opcoes["poolclass"] = StaticPool
        return opcoes
    return {"pool_pre_ping": True}


DATABASE_URL = obter_configuracao().url_banco
engine = create_engine(DATABASE_URL, **_opcoes_do_engine(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def criar_tabelas() -> None:
    """Importa os modelos e cria as tabelas."""
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def obter_sessao():
    """Entrega uma sessão por uso e fecha ao terminar."""
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()