"""Funções para trabalhar com datas e horários."""
from datetime import datetime, timezone


def agora_utc() -> datetime:
    """Retorna o momento atual com fuso UTC."""
    return datetime.now(timezone.utc)