"""Operações de cadastro, login e identificação de usuários."""
from dataclasses import dataclass

from app.core.exceptions import CredenciaisInvalidas, EmailJaCadastrado, TokenInvalido
from app.core.security import HashDeSenha, TokenEmitido, TokenJWT
from app.models.usuario import Usuario
from app.repositories.usuario import UsuarioRepositorio


@dataclass(frozen=True)
class Sessao:
    """Resultado de um login: usuário autenticado e token emitido."""
    usuario: Usuario
    token: TokenEmitido


class UsuarioServico:
    def __init__(self, repositorio: UsuarioRepositorio, hasher: HashDeSenha, tokens: TokenJWT | None = None):
        self._repositorio = repositorio
        self._hasher = hasher
        self._tokens = tokens

    def cadastrar(self, nome: str, email: str, senha: str) -> Usuario:
        if self._repositorio.email_existe(email):
            raise EmailJaCadastrado()
        usuario = Usuario(nome=nome, email=email)
        usuario.definir_senha(senha, self._hasher)
        return self._repositorio.salvar(usuario)

    def autenticar(self, email: str, senha: str) -> Usuario:
        usuario = self._repositorio.buscar_por_email(email)
        if usuario is None or not usuario.senha_confere(senha, self._hasher):
            raise CredenciaisInvalidas()
        return usuario

    def entrar(self, email: str, senha: str) -> Sessao:
        usuario = self.autenticar(email, senha)
        return Sessao(usuario=usuario, token=self._exigir_tokens().emitir(usuario.id))

    def usuario_do_token(self, token: str) -> Usuario:
        usuario_id = self._exigir_tokens().ler(token)
        usuario = self._repositorio.buscar_por_id(usuario_id)
        if usuario is None:
            raise TokenInvalido()
        return usuario

    def _exigir_tokens(self) -> TokenJWT:
        if self._tokens is None:
            raise RuntimeError("O serviço foi criado sem um emissor de tokens.")
        return self._tokens
