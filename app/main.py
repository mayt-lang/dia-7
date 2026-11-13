"""Ponto de entrada: cria o app, registra as rotas e traduz erros em HTTP."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers import tasks, usuarios
from app.core.config import obter_configuracao
from app.core.exceptions import (
    AcessoNaoAutorizado,
    EmailJaCadastrado,
    ErroDeDominio,
    NaoAutenticado,
    RecursoNaoEncontrado,
    RegraDeNegocioViolada,
    ValorInvalido,
)
from app.db.database import criar_tabelas

STATUS_POR_ERRO: tuple[tuple[type[ErroDeDominio], int], ...] = (
    (RecursoNaoEncontrado, 404),
    (EmailJaCadastrado, 409),
    (NaoAutenticado, 401),
    (AcessoNaoAutorizado, 403),
    (RegraDeNegocioViolada, 422),
    (ErroDeDominio, 400),
)


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncIterator[None]:
    """Confere a configuração e prepara o segredo JWT com na subida da aplicação.

    segredo_jwt é chamado aqui para garantir que JWT_SECRET, a API se
    recusa a subir com uma mensagem explicando o que fazer e subir
    e só falhar no primeiro login.
    """
    obter_configuracao().segredo_jwt()
    criar_tabelas()
    yield


app = FastAPI(
    title="Todo List API",
    description="Backend do Todo List - Curso Desenvolvedor Full Stack (SENAC).",
    version="0.10.0",
    lifespan=ciclo_de_vida,
)


@app.exception_handler(ErroDeDominio)
async def tratar_erro_de_dominio(
    _request: Request, excecao: ErroDeDominio
) -> JSONResponse:
    """Converte qualquer erro de domínio na resposta HTTP correspondente."""
    codigo = next(
        (codigo for tipo, codigo in STATUS_POR_ERRO if isinstance(excecao, tipo)), 400
    )
    # O padrão HTTP pede que toda resposta 401 diga como se autenticar.
    cabecalhos = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(
        status_code=codigo, content={"detail": excecao.mensagem}, headers=cabecalhos
    )


def _mensagem_de_validacao(erro: dict[str, Any]) -> tuple[str, str]:
    """Traduz um erro do Pydantic em campo, mensagem em português."""
    campo = str(erro.get("loc", [""])[-1])
    tipo = erro.get("type", "")
    ctx = erro.get("ctx", {})

    mensagens = {
        "missing": f"O campo '{campo}' é obrigatório.",
        "string_too_short": (
            f"O campo '{campo}' precisa ter pelo menos "
            f"{ctx.get('min_length')} caractere(s)."
        ),
        "string_too_long": f"O campo '{campo}' pode ter no máximo "
        f"{ctx.get('max_length')} caracteres.",
        "enum": f"Valor inválido para '{campo}'. Valores aceitos: "
        f"{str(ctx.get('expected', '')).replace(' or ', ', ')}.",
        "date_parsing": f"Data inválida em '{campo}'. Use o formato AAAA-MM-DD.",
        "date_from_datetime_parsing": f"Data inválida em '{campo}'. Use o formato AAAA-MM-DD.",
        "int_parsing": f"O campo '{campo}' precisa ser um número inteiro.",
        "greater_than_equal": f"O campo '{campo}' precisa ser no mínimo {ctx.get('ge')}.",
        "less_than_equal": f"O campo '{campo}' pode ser no máximo {ctx.get('le')}.",
        "json_invalid": "O corpo da requisição não é um JSON válido.",
    }

    if tipo == "value_error":
        if campo == "email":
            return campo, "E-mail inválido."
        # Mensagens dos nossos próprios validadores já estão em português.
        return campo, str(erro.get("msg", "")).removeprefix("Value error, ")

    return campo, mensagens.get(tipo, f"Valor inválido em '{campo}'.")


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(
    _request: Request, excecao: RequestValidationError
) -> JSONResponse:
    """Responde 422 com 'detail' sempre em TEXTO, em português.

    O padrão do FastAPI devolve 'detail' como uma lista de objetos em inglês -
    difícil de mostrar ao usuário. Aqui 'detail' traz a primeira mensagem
    pronta para exibir, e 'errors' traz a lista completa, campo a campo.
    """
    erros = [
        {"campo": campo, "mensagem": mensagem}
        for campo, mensagem in (
            _mensagem_de_validacao(erro) for erro in excecao.errors()
        )
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": erros[0]["mensagem"] if erros else "Dados inválidos.", "errors": erros},
    )


app.include_router(usuarios.router)
app.include_router(tasks.router)


@app.get("/", summary="Verificar se a API está no ar")
def raiz() -> dict[str, str]:
    """Confirma que a API está ativa e indica onde está a documentação."""
    return {"mensagem": "Todo List API no ar", "documentacao": "/docs"}