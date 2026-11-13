# Entidade Tarefa (todo)
"""Entidade Tarefa: dados e regras de uma tarefa."""

from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, validates

from app.core.data import agora_utc
from app.core.exceptions import TituloObrigatorio, ValorInvalido
from app.db.database import Base
from app.models.enums import PrioridadeTarefa, StatusTarefa


class Tarefa(Base):
    """Tarefa pertencente a um usuário."""

    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )

    titulo = Column(String(200), nullable=False)
    status = Column(String(15), nullable=False)
    prioridade = Column(String(20), nullable=False)
    prazo = Column(Date, nullable=True)

    criado_em = Column(
        DateTime(timezone=True), nullable=False, default=agora_utc
    )

    atualizado_em = Column(
        DateTime(timezone=True), nullable=False, default=agora_utc,
        onupdate=agora_utc
    )

    concluido_em = Column(
        "concluido_em", DateTime(timezone=True), nullable=True
    )

    usuario = relationship("Usuario", back_populates="tarefas")

    def __init__(
        self,
        usuario_id: int,
        titulo: str,
        prioridade: PrioridadeTarefa | str = PrioridadeTarefa.MEDIA,
        prazo: date | None = None,
    ):
        """Cria uma tarefa sempre pendente e sem data de conclusão."""

        self.usuario_id = usuario_id
        self.titulo = titulo
        self.prioridade = prioridade
        self.prazo = prazo
        self.status = StatusTarefa.PENDENTE.value
        self.concluido_em = None

    # --------------------------------------------------
    # leitura

    @hybrid_property
    def status(self) -> StatusTarefa:
        """Retorna o status como enum, sem perder a consulta legível."""
        return StatusTarefa(self._status)

    @status.setter
    def status(self, valor: StatusTarefa | str) -> None:
        self._status = StatusTarefa(valor).value

    @status.expression
    def status(cls):
        """Versão da propriedade usada dentro de consultas SQL."""
        return cls._status

    @property
    def concluido_em(self) -> date | None:
        """Retorna a data em que a tarefa está pendente."""
        return self._concluido_em

    @concluido_em.setter
    def concluido_em(self, valor: date | None) -> None:
        self._concluido_em = valor

    # --------------------------------------------------
    # operações

    def concluir(self, agora: datetime | None = None) -> None:
        """Conclui a tarefa e registra o momento."""

        if self.status == StatusTarefa.CONCLUIDA.value:
            return

        self.status = StatusTarefa.CONCLUIDA.value
        self.concluido_em = agora or agora_utc()

    def reabrir(self) -> None:
        """Reabre a tarefa pendente e apaga a data de conclusão."""

        if self.status == StatusTarefa.PENDENTE.value:
            return

        self.status = StatusTarefa.PENDENTE.value
        self.concluido_em = None

    def definir_status(
        self, novo_status: StatusTarefa | str, agora: datetime | None = None
    ) -> None:
        """Aplica o status informado pela operação correspondente."""

        status = StatusTarefa(novo_status)

        if status == StatusTarefa.CONCLUIDA:
            self.concluir(agora)
        else:
            self.reabrir()

    def pertence(self, usuario_id: int) -> bool:
        """Informa se a tarefa é de determinado usuário."""

        return self.usuario_id == usuario_id

    # --------------------------------------------------
    # validação

    @validates("titulo")
    def _validar_titulo(self, campo: str, valor: str) -> str:
        """Recusa título vazio, aqui e em qualquer ponto do programa."""

        if valor is None or not valor.strip():
            raise TituloObrigatorio()

        return valor.strip()

    @validates("prioridade")
    def _validar_prioridade(self, campo: str, valor: object) -> str:
        """Aceita o enum ou o texto correspondente, e grava sempre o texto."""

        try:
            return PrioridadeTarefa(valor).value
        except ValueError as erro:
            permitidos = ", ".join(p.value for p in PrioridadeTarefa)
            raise ValorInvalido(
                f"Prioridade inválida. Valores aceitos: {permitidos}."
            ) from erro

    def __repr__(self) -> str:
        return (
            f"<Tarefa(id={self.id}, título={self.titulo!r}, "
            f"status={self.status})>"
        )