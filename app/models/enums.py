"""Vocabulário único de status e prioridades das tarefas."""
from enum import Enum


class StatusTarefa(str, Enum):
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"


class PrioridadeTarefa(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

    @property
    def peso(self) -> int:
        return _PESOS[self]

    @classmethod
    def mapa_de_pesos(cls) -> dict[str, int]:
        return {prioridade.value: peso for prioridade, peso in _PESOS.items()}


_PESOS = {
    PrioridadeTarefa.URGENTE: 0,
    PrioridadeTarefa.ALTA: 1,
    PrioridadeTarefa.MEDIA: 2,
    PrioridadeTarefa.BAIXA: 3,
}
