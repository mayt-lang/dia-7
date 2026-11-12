"""Entidade de usuário e suas regras básicas."""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship, validates

from app.core.datas import agora_utc
from app.core.exceptions import ValorInvalido
from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    _senha_hash = Column("senha_hash", String(255), nullable=False)
    criado_em = Column(DateTime(timezone=True), default=agora_utc, nullable=False)
    tarefas = relationship("Tarefa", back_populates="usuario", cascade="all, delete-orphan")

    def __init__(self, *, nome: str, email: str):
        self.nome = nome
        self.email = self.normalizar_email(email)

    @staticmethod
    def normalizar_email(email: str) -> str:
        return email.strip().lower()

    def definir_senha(self, senha: str, hasher) -> None:
        self._senha_hash = hasher.gerar(senha)

    def senha_confere(self, senha: str, hasher) -> bool:
        return hasher.verificar(senha, self._senha_hash)

    @validates("nome")
    def validar_nome(self, chave, nome: str) -> str:
        nome_normalizado = nome.strip()
        if not nome_normalizado:
            raise ValorInvalido("O nome do usuário não pode ficar vazio.")
        if len(nome_normalizado) > 120:
            raise ValorInvalido("O nome deve ter no máximo 120 caracteres.")
        return nome_normalizado

    def __repr__(self) -> str:
        return f"Usuario(id={self.id!r}, nome={self.nome!r}, email={self.email!r})"
