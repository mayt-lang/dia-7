
"""Provedores de dependência: montam os objetos que as rotas usam."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import obter_configuracao
from app.core.exceptions import NaoAutenticado
from app.core.security import HashBcrypt, TokenJWT
from app.db.database import obter_sessao
from app.models import Usuario
from app.repositories import TarefaRepositorio, UsuarioRepositorio
from app.services import TarefaServico, UsuarioServico

_esquema_bearer = HTTPBearer(auto_error=False)


def obter_hasher() -> HashBcrypt:
    return HashBcrypt()


def obter_tokens() -> TokenJWT:
    config = obter_configuracao()
    return TokenJWT(config.segredo_jwt(), config.jwt_expira_minutos)


def obter_usuario_servico(
    sessao: Session = Depends(obter_sessao),
    hasher: HashBcrypt = Depends(obter_hasher),
    tokens: TokenJWT = Depends(obter_tokens),
) -> UsuarioServico:
    return UsuarioServico(UsuarioRepositorio(sessao), hasher, tokens)


def obter_tarefa_servico(sessao: Session = Depends(obter_sessao)) -> TarefaServico:
    return TarefaServico(TarefaRepositorio(sessao))


ServicoUsuario = Annotated[UsuarioServico, Depends(obter_usuario_servico)]


def obter_usuario_atual(
    credenciais: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_esquema_bearer)
    ],
    servico: ServicoUsuario,
) -> Usuario:
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise NaoAutenticado()
    return servico.usuario_do_token(credenciais.credentials)


# Use usuario: UsuarioAtual nas rotas que exigem autenticação.
UsuarioAtual = Annotated[Usuario, Depends(obter_usuario_atual)]
