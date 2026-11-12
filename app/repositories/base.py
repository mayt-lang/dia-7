"""Operações comuns aos repositórios."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

Entidade = TypeVar("Entidade")


class RepositorioBase(ABC, Generic[Entidade]):
    def __init__(self, sessao: Session):
        self._sessao = sessao

    @property
    @abstractmethod
    def modelo(self):
        """Classe de modelo administrada pelo repositório."""
        raise NotImplementedError

    def buscar_por_id(self, identificador: int):
        return self._sessao.get(self.modelo, identificador)

    def salvar(self, entidade: Entidade) -> Entidade:
        try:
            self._sessao.add(entidade)
            self._sessao.commit()
            self._sessao.refresh(entidade)
            return entidade
        except Exception:
            self._sessao.rollback()
            raise

    def remover(self, entidade: Entidade) -> None:
        try:
            self._sessao.delete(entidade)
            self._sessao.commit()
        except Exception:
            self._sessao.rollback()
            raise