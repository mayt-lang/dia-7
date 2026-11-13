def listar(self, filtro: FiltroDeTarefas) -> list[Tarefa]:
    """Lista as tarefas conforme os critérios informados."""
    return self._tarefas.listar(filtro)

def buscar(self, tarefa_id: int, usuario_id: int) -> Tarefa:
    """Devolve uma tarefa do usuário.

    Raises:
        TarefaNaoEncontrada: se não existir tarefa com este id.
        AcessoNaoAutorizado: se a tarefa for de outro usuário.
    """
    tarefa = self._tarefas.buscar_por_id(tarefa_id)
    if tarefa is None:
        raise TarefaNaoEncontrada()
    if not tarefa.pertence_a(usuario_id):
        raise AcessoNaoAutorizado()
    return tarefa

def atualizar(
    self,
    tarefa_id: int,
    usuario_id: int,
    alteracoes: AlteracoesDaTarefa,
) -> Tarefa:
    """Aplica as alterações informadas e devolve a tarefa atualizada.

    A RN-03 não aparece aqui: a mudança de status é delegada a
    Tarefa.definir_status, que sabe concluir, reabrir e preservar a data
    original. O serviço apenas encaminha a intenção.

    Raises:
        TarefaNaoEncontrada: se não existir tarefa com este id.
        AcessoNaoAutorizado: se a tarefa for de outro usuário.
    """
    tarefa = self.buscar(tarefa_id, usuario_id)

    if alteracoes.informado("titulo"):
        tarefa.titulo = alteracoes.titulo
    if alteracoes.informado("prioridade"):
        tarefa.prioridade = alteracoes.prioridade
    if alteracoes.informado("prazo"):
        tarefa.prazo = alteracoes.prazo
    if alteracoes.informado("status"):
        tarefa.definir_status(StatusTarefa(alteracoes.status))

    return self._tarefas.salvar(tarefa)

def remover(self, tarefa_id: int, usuario_id: int) -> None:
    """Remove a tarefa definitivamente.

    Raises:
        TarefaNaoEncontrada: se não existir tarefa com este id.
        AcessoNaoAutorizado: se a tarefa for de outro usuário.
    """
    self._tarefas.remover(self.buscar(tarefa_id, usuario_id))


def listar_tasks(
    usuario: UsuarioAtual,
    servico: Servico,
    response: Response,
    status_tarefa: Annotated[StatusTarefa | None, Query(alias="status")] = None,
    prioridade: Annotated[PrioridadeTarefa | None, Query()] = None,
    prazo_ate: Annotated[
        date | None,
        Query(
            alias="prazoAte",
            description="Somente tarefas com prazo até esta data",
        ),
    ] = None,
    busca: Annotated[
        str | None,
        Query(
            max_length=200,
            description="Texto contido no título (sem diferenciar maiúsculas)",
        ),
    ] = None,
) -> list[TarefaOut]:
    """Lista as tarefas do usuário logado, com filtros opcionais."""
    filtro = FiltroDeTarefas(
        usuario_id=usuario.id,
        status=status_tarefa,
        prioridade=prioridade,
        prazo_ate=prazo_ate,
        busca=(busca or "").strip() or None,
    )
    tarefas = servico.listar(filtro)
    response.headers["X-Total-Count"] = str(len(tarefas))
    return tarefas


@router.get(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Consultar uma tarefa",
    responses=RESPOSTAS_DE_UMA_TAREFA,
)
def buscar_task(
    tarefa_id: int,
    usuario: UsuarioAtual,
    servico: Servico,
) -> TarefaOut:
    """Devolve uma tarefa do usuário logado."""
    return servico.buscar(tarefa_id, usuario.id)


@router.patch(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Atualizar tarefa",
    responses=RESPOSTAS_DE_UMA_TAREFA,
)
def atualizar_task(
    tarefa_id: int,
    dados: TarefaUpdate,
    usuario: UsuarioAtual,
    servico: Servico,
) -> TarefaOut:
    """Atualiza parcialmente uma tarefa."""
    return servico.atualizar(tarefa_id, usuario.id, _montar_alteracoes(dados))


@router.delete(
    "/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover tarefa",
    responses=RESPOSTAS_DE_UMA_TAREFA,
)
def remover_task(
    tarefa_id: int,
    usuario: UsuarioAtual,
    servico: Servico,
) -> Response:
    """Remove uma tarefa definitivamente."""
    servico.remover(tarefa_id, usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)