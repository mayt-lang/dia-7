"""Contratos JSON de usuário e de sessão (login)."""
from pydantic import EmailStr, Field, field_validator

from app.core.security import LIMITE_BYTES_SENHA
from app.schemas.base import DataHoraUTC, EsquemaDeEntrada, EsquemaDeSaida


class UsuarioCreate(EsquemaDeEntrada):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("O nome do usuário não pode ficar vazio.")
        return valor

    @field_validator("senha")
    @classmethod
    def validar_tamanho_senha(cls, senha: str) -> str:
        if len(senha.encode("utf-8")) > LIMITE_BYTES_SENHA:
            raise ValueError("A senha não pode ultrapassar 72 bytes em UTF-8.")
        return senha


class UsuarioLogin(EsquemaDeEntrada):
    email: EmailStr
    senha: str


class UsuarioOut(EsquemaDeSaida):
    id: int
    nome: str
    email: EmailStr
    criado_em: DataHoraUTC


class SessaoOut(EsquemaDeSaida):
    access_token: str
    token_type: str = "bearer"
    expira_em: DataHoraUTC
    usuario: UsuarioOut
