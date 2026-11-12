"""Leitura e validação das configurações da aplicação."""
from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


class ConfiguracaoInvalida(RuntimeError):
    """Erro lançado quando uma configuração obrigatória está ausente ou inválida."""


@dataclass(frozen=True)
class Configuracao:
    """Configurações imutáveis carregadas do ambiente."""
    database_url: str = ""
    jwt_secret: str = ""
    jwt_expira_minutos: int = 120

    @classmethod
    def do_ambiente(cls) -> "Configuracao":
        try:
            minutos = int(os.getenv("JWT_EXPIRA_MINUTOS", "120"))
        except ValueError as erro:
            raise ConfiguracaoInvalida("JWT_EXPIRA_MINUTOS precisa ser um número inteiro.") from erro
        return cls(
            database_url=os.getenv("DATABASE_URL", "").strip(),
            jwt_secret=os.getenv("JWT_SECRET", "").strip(),
            jwt_expira_minutos=minutos,
        )

    @property
    def url_banco(self) -> str:
        if not self.database_url:
            raise ConfiguracaoInvalida("DATABASE_URL não foi definida. Copie .env.example para .env e configure o banco.")
        return self.database_url

    def segredo_jwt(self) -> str:
        if len(self.jwt_secret) < 32:
            raise ConfiguracaoInvalida("JWT_SECRET precisa ter pelo menos 32 caracteres. Gere uma chave secreta e coloque no arquivo .env.")
        if self.jwt_expira_minutos <= 0:
            raise ConfiguracaoInvalida("JWT_EXPIRA_MINUTOS precisa ser maior que zero.")
        return self.jwt_secret


@lru_cache(maxsize=1)
def obter_configuracao() -> Configuracao:
    return Configuracao.do_ambiente()
