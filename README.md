# Todo List API — Dias 2 a 6

Projeto back-end em Python com FastAPI, SQLAlchemy, SQLite/PostgreSQL, cadastro de usuários, login JWT, rota protegida e criação de tarefas.

> O pacote de manuais enviado começa no Dia 2. Não foi fornecido manual do Dia 1; por isso, a estrutura inicial que já existia no ZIP foi mantida como base e revisada junto aos dias 2 a 6.

## Requisitos
- Python 3.11 ou superior (o projeto foi iniciado com Python 3.14).
- Git opcional.

## Preparação no Windows
Abra o terminal na pasta onde está `requirements.txt` e execute:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Abra `.env` e troque `JWT_SECRET` por uma chave aleatória com pelo menos 32 caracteres. Não compartilhe esse valor e nunca envie `.env` ao GitHub. O banco local SQLite é criado automaticamente.

## Executar a API

```powershell
uvicorn app.main:app --reload
```

Abra http://127.0.0.1:8000/docs para usar a documentação interativa.

## Caminho de teste no /docs
1. `POST /usuarios`: cadastre nome, e-mail e senha.
2. `POST /usuarios/login`: entre com o mesmo e-mail e senha e copie `accessToken`.
3. Clique em **Authorize**, informe o token (ou `Bearer ` seguido do token, conforme a janela) e confirme.
4. `GET /usuarios/me`: consulte o usuário autenticado.
5. `POST /tasks`: crie uma tarefa com título e, opcionalmente, prioridade e prazo. O dono vem do token e o status sempre começa como `pendente`.

## Testes

```powershell
pytest -q
```

## Rotas implementadas até o Dia 6
- `GET /` — status da API.
- `POST /usuarios` — cadastro com e-mail único.
- `POST /usuarios/login` — login e emissão de JWT.
- `GET /usuarios/me` — perfil do usuário autenticado.
- `POST /tasks` — criação de tarefa protegida por JWT.

Listagem, edição, conclusão e exclusão de tarefas pertencem aos próximos dias e ainda não foram incluídas.

## Segurança e GitHub
O `.gitignore` exclui `.env`, ambientes virtuais, arquivos `.db`, caches e configurações locais. Antes de enviar ao GitHub, confira `git status` e certifique-se de que `.env` e `todo_list.db` não aparecem.
