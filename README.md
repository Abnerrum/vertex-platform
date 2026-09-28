# Vertex Platform

Plataforma de operações e automação para empresas que já têm ferramentas demais e processos manuais de menos. Em vez de substituir o que a empresa usa, a proposta da Vertex é centralizar a operação, automatizar tarefas repetitivas e transformar dados em decisão.

> **Vertex** e **Vertex Tech Solutions** seguem como nomes provisórios até a definição da marca definitiva.

## Vertex Core — MVP demonstrável

Fluxo atual:

Login → Dashboard → Clientes → Projetos → Serviços/OS → Histórico

### Status atual — v0.6.0
- API FastAPI com documentação interativa
- SQLite para demonstração rápida e PostgreSQL via Docker
- Login JWT e primeiro administrador via bootstrap
- CRUD de clientes
- CRUD de projetos vinculados aos clientes
- CRUD de Ordens de Serviço
- Prioridade, status, prazo e histórico automático de OS
- Dashboard com indicadores reais
- **Frontend demonstrativo conectado à API real**
- Cadastro de clientes, projetos e OS pela interface
- Avanço de status de OS pela interface
- Consulta do histórico da OS pela interface
- Testes automatizados com GitHub Actions

## Executar para apresentação

### Terminal 1 — API

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`  
Swagger: `http://127.0.0.1:8000/docs`

### Terminal 2 — interface

```powershell
cd docs
python -m http.server 5500
```

Interface: `http://127.0.0.1:5500`

No primeiro acesso, use a opção **Primeiro acesso** na tela de login para criar o administrador. Depois, todos os dados cadastrados na interface são gravados pela API.

## Visão do produto

| Módulo | O que faz | Situação |
| --- | --- | --- |
| **Vertex Core** | Usuários, clientes, projetos, OS, histórico e dashboard | MVP demonstrável |
| **Vertex Flow** | Automações, SLA, atribuição e alertas | Planejado |
| **Vertex Data** | Indicadores, relatórios e análises | Planejado |
| **Vertex Connect** | Integrações e APIs | Planejado |
| **Vertex Assistant** | Consulta em linguagem natural sobre dados autorizados | Planejado |
| **Vertex Compliance Hub** | Documentos, contratos e vencimentos | Futuro |

## Testes

```powershell
cd backend
pytest -q
```

> Projeto em desenvolvimento. Não use credenciais reais no ambiente demonstrativo e troque `SECRET_KEY` antes de produção.
