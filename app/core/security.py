"""Hash de senhas com bcrypt e emissão/leitura de tokens JWT."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.exceptions import TokenInvalido

LIMITE_BYTES_SENHA = 72


class HashDeSenha(ABC):
    """Contrato para gerar e verificar hashes de senha."""
    @abstractmethod
    def gerar(self, senha: str) -> str:
        """Gera um hash seguro para a senha."""

    @abstractmethod
    def verificar(self, senha: str, hash_armazenado: str) -> bool:
        """Confere uma senha com um hash já armazenado."""


class HashBcrypt(HashDeSenha):
    """Implementação de hash usando bcrypt."""
    def gerar(self, senha: str) -> str:
        senha_bytes = senha.encode("utf-8")
        if len(senha_bytes) > LIMITE_BYTES_SENHA:
            raise ValueError("A senha não pode ultrapassar 72 bytes em UTF-8.")
        return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")

    def verificar(self, senha: str, hash_armazenado: str) -> bool:
        senha_bytes = senha.encode("utf-8")
        if len(senha_bytes) > LIMITE_BYTES_SENHA:
            return False
        try:
            return bcrypt.checkpw(senha_bytes, hash_armazenado.encode("utf-8"))
        except (ValueError, TypeError):
            return False


@dataclass(frozen=True)
class TokenEmitido:
    """Representa o JWT emitido e seu horário de expiração."""
    valor: str
    expira_em: datetime


class TokenJWT:
    """Emite e valida tokens JWT assinados com HS256."""
    ALGORITMO = "HS256"

    def __init__(self, segredo: str, expira_minutos: int):
        self._segredo = segredo
        self._validade = timedelta(minutes=expira_minutos)

    def emitir(self, usuario_id: int, agora: datetime | None = None) -> TokenEmitido:
        instante = agora or datetime.now(timezone.utc)
        if instante.tzinfo is None:
            instante = instante.replace(tzinfo=timezone.utc)
        expira_em = instante + self._validade
        conteudo = {"sub": str(usuario_id), "exp": expira_em}
        valor = jwt.encode(conteudo, self._segredo, algorithm=self.ALGORITMO)
        return TokenEmitido(valor=valor, expira_em=expira_em)

    def ler(self, token: str) -> int:
        try:
            conteudo = jwt.decode(
                token,
                self._segredo,
                algorithms=[self.ALGORITMO],
                options={"require": ["sub", "exp"]},
            )
            return int(conteudo["sub"])
        except jwt.ExpiredSignatureError as erro:
            raise TokenInvalido("Sessão expirada. Entre novamente.") from erro
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as erro:
            raise TokenInvalido() from erro
