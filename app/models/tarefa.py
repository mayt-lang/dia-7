"""Entidade Tarefa: pertence a um usuário e sempre nasce pendente."""
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from app.core.datas import agora_utc
from app.core.exceptions import TituloObrigatorio, ValorInvalido
from app.db.database import Base
from app.models.enums import PrioridadeTarefa, StatusTarefa


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo = Column(String(200), nullable=False)
    _status = Column("status", String(20), nullable=False, default=StatusTarefa.PENDENTE.value)
    prioridade = Column(String(20), nullable=False, default=PrioridadeTarefa.MEDIA.value)
    prazo = Column(Date, nullable=True)
    criado_em = Column(DateTime(timezone=True), default=agora_utc, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), default=agora_utc, onupdate=agora_utc, nullable=False)
    _concluido_em = Column("concluido_em", DateTime(timezone=True), nullable=True)
    usuario = relationship("Usuario", back_populates="tarefas")

    def __init__(self, *, usuario_id: int, titulo: str, prioridade=PrioridadeTarefa.MEDIA, prazo=None):
        self.usuario_id = usuario_id
        self.titulo = titulo
        self._status = StatusTarefa.PENDENTE.value
        self.prioridade = prioridade
        self.prazo = prazo
        self._concluido_em = None

    @property
    def status(self) -> StatusTarefa:
        return StatusTarefa(self._status)

    @property
    def concluido_em(self):
        return self._concluido_em

    def pertence_a(self, usuario_id: int) -> bool:
        return self.usuario_id == usuario_id

    @validates("titulo")
    def validar_titulo(self, chave, titulo: str) -> str:
        titulo_normalizado = titulo.strip()
        if not titulo_normalizado:
            raise TituloObrigatorio()
        if len(titulo_normalizado) > 200:
            raise ValorInvalido("O título deve ter no máximo 200 caracteres.")
        return titulo_normalizado

    @validates("prioridade")
    def validar_prioridade(self, chave, prioridade) -> str:
        try:
            return PrioridadeTarefa(prioridade).value
        except ValueError as erro:
            aceitas = ", ".join(item.value for item in PrioridadeTarefa)
            raise ValorInvalido(f"Prioridade inválida. Valores aceitos: {aceitas}.") from erro

    def __repr__(self) -> str:
        return f"Tarefa(id={self.id!r}, usuario_id={self.usuario_id!r}, titulo={self.titulo!r})"
