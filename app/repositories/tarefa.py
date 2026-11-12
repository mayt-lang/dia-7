
"""Repositório de persistência das tarefas."""

from __future__ import annotations

from app.models.tarefa import Tarefa
from app.repositories.base import RepositorioBase


class TarefaRepositorio(RepositorioBase[Tarefa]):
    @property
    def modelo(self):
        return Tarefa

    def listar(self, usuario_id: int) -> list[Tarefa]:
        """Lista somente as tarefas do usuário informado.

        O filtro é feito diretamente no banco para não carregar
        tarefas pertencentes a outros usuários.
        """
        return (
            self._sessao.query(Tarefa)
            .filter(Tarefa.usuario_id == usuario_id)
            # O id desempata tarefas criadas no mesmo instante.
            .order_by(Tarefa.criado_em.desc(), Tarefa.id.desc())
            .all()
        )
