"""Rotas de cadastro, login e consulta do usuário autenticado."""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import UsuarioAtual, obter_usuario_servico
from app.schemas import SessaoOut, UsuarioCreate, UsuarioLogin, UsuarioOut
from app.services import UsuarioServico

router = APIRouter(prefix="/usuarios", tags=["Usuários"])
Servico = Annotated[UsuarioServico, Depends(obter_usuario_servico)]


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Cadastrar usuário", responses={409: {"description": "E-mail já cadastrado."}})
def cadastrar_usuario(dados: UsuarioCreate, servico: Servico) -> UsuarioOut:
    return servico.cadastrar(dados.nome, str(dados.email), dados.senha)


@router.post("/login", response_model=SessaoOut, summary="Entrar no sistema",
             responses={401: {"description": "E-mail ou senha incorretos."}})
def login(dados: UsuarioLogin, servico: Servico) -> SessaoOut:
    """No /docs, use o accessToken retornado no botão Authorize."""
    sessao = servico.entrar(str(dados.email), dados.senha)
    return SessaoOut(
        access_token=sessao.token.valor,
        expira_em=sessao.token.expira_em,
        usuario=sessao.usuario,
    )


@router.get("/me", response_model=UsuarioOut, summary="Consultar o usuário logado",
            responses={401: {"description": "É preciso entrar na conta para continuar."}})
def quem_sou_eu(usuario: UsuarioAtual) -> UsuarioOut:
    return usuario
