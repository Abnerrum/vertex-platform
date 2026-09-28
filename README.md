# Vertex Platform

Plataforma de operações e automação para empresas que já têm ferramentas demais e processos manuais de menos. Em vez de substituir o que a empresa usa, a proposta da Vertex é centralizar a operação, automatizar tarefas repetitivas e transformar dados em decisão.

> **Vertex** e **Vertex Tech Solutions** seguem como nomes provisórios até a definição da marca definitiva.

## Vertex Core — MVP demonstrável

Fluxo atual:

Login → Dashboard → Clientes → Projetos → Serviços/OS → Histórico

### Status atual — v0.6.1
- API FastAPI com documentação interativa
- SQLite para demonstração rápida e PostgreSQL via Docker
- Login JWT e primeiro administrador via bootstrap
- CRUD de clientes
- CRUD de projetos vinculados aos clientes
- CRUD de Ordens de Serviço
- Prioridade, status, prazo e histórico automático de OS
- Dashboard com indicadores reais
- Frontend demonstrativo conectado à API real
- A própria API serve a interface em `/app/`, evitando erro de conexão na demo local
- Cadastro de clientes, projetos e OS pela interface
- Avanço de status de OS pela interface
- Consulta do histórico da OS pela interface
- Testes automatizados com GitHub Actions

## Executar para apresentação

### Opção mais simples no Windows

Na raiz do projeto, dê dois cliques em:

`INICIAR_DEMO.bat`

Ele inicia a API e abre automaticamente:

`http://127.0.0.1:8000/app/`

### Pelo terminal

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Abra:

`http://127.0.0.1:8000/app/`

Swagger:

`http://127.0.0.1:8000/docs`

No primeiro acesso, use a opção **Primeiro acesso** para criar o administrador. Depois, todos os dados cadastrados na interface são gravados pela API.

> A página publicada no Netlify é apenas o frontend estático. Sem um backend público ela não consegue cadastrar usuários. Para a apresentação funcional local, use `http://127.0.0.1:8000/app/`.

## Testes

```powershell
cd backend
pytest -q
```

> Projeto em desenvolvimento. Não use credenciais reais no ambiente demonstrativo e troque `SECRET_KEY` antes de produção.
