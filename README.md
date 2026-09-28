# Vertex Platform

Plataforma de operações e automação para empresas que já têm ferramentas demais e processos manuais de menos. Em vez de substituir o que a empresa usa (ERP, planilhas, WhatsApp, sistemas isolados), a proposta da Vertex é centralizar a operação, automatizar o que é repetitivo e transformar os dados em decisão.

> **Vertex** e **Vertex Tech Solutions** seguem como nomes provisórios até a definição da marca definitiva.

## Visão do produto

| Módulo | O que faz | Situação |
| --- | --- | --- |
| **Vertex Core** | Usuários, clientes, projetos, OS, status, histórico e dashboard | **Em desenvolvimento** (este repositório) |
| **Vertex Flow** | Motor de automações e regras de processo (SLA, atribuição, alertas) | Planejado |
| **Vertex Data** | Indicadores, relatórios e análises da operação | Planejado |
| **Vertex Connect** | Integrações e APIs com os sistemas que a empresa já usa | Planejado |
| **Vertex Assistant** | Consulta em linguagem natural sobre os dados que o usuário pode ver | Planejado |
| **Vertex Compliance Hub** | Documentos, contratos, certificados, vencimentos e obrigações | Ideia futura |

O foco atual é inteiro no **Vertex Core**: sem ele, nenhum dos outros módulos tem base sobre a qual rodar.

## Fase 1 — MVP do Core

Objetivo: fluxo completo funcionando de ponta a ponta.

Login → Dashboard → Clientes → Projetos → Serviços/OS → Histórico

### Status atual — v0.5.0
- API FastAPI com documentação interativa
- Docker/PostgreSQL para o banco
- Primeiro administrador via bootstrap
- Login JWT
- Perfis: `admin`, `commercial`, `technical`, `finance`
- CRUD de clientes protegido por autenticação
- CRUD de projetos vinculado aos clientes
- CRUD de Ordens de Serviço vinculado a cliente e projeto
- Responsável, prioridade, prazo e status nas OS
- Histórico automático das principais alterações de OS
- Filtros de clientes, projetos e ordens de serviço
- Dashboard com totais de usuários, clientes, projetos e OS
- Testes de saúde, autenticação, clientes, projetos e OS

### Próximos passos
- Permissões por perfil nas rotas
- Frontend React consumindo a API real
- Dashboard real com indicadores
- Deploy integrado

## Stack
- Backend: Python + FastAPI
- Banco: PostgreSQL (SQLite disponível para desenvolvimento)
- ORM: SQLAlchemy
- Autenticação: JWT + perfis de acesso
- Testes: Pytest
- Containers: Docker
- Frontend: protótipo estático hoje; React na integração

## Executar a API

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Linux/macOS: cp .env.example .env
uvicorn app.main:app --reload
```

O padrão de desenvolvimento usa SQLite e não exige nenhum serviço externo. A documentação interativa fica em `http://127.0.0.1:8000/docs`.

### Usar PostgreSQL

```bash
docker compose up -d db
```

Depois copie o `.env.example` da raiz para `backend/.env` — ele já aponta para o banco do container.

## Criar o primeiro administrador

Com o banco vazio, use uma única vez:

```http
POST /api/v1/auth/bootstrap
```

```json
{
  "name": "Administrador",
  "email": "admin@example.com",
  "password": "troque-por-uma-senha-forte"
}
```

Depois, faça login em `POST /api/v1/auth/login`. As rotas de clientes, projetos, OS e dashboard exigem o token Bearer retornado pelo login.

## Principais rotas atuais
- `/api/v1/auth/*` — autenticação e usuários
- `/api/v1/clients` — clientes
- `/api/v1/projects` — projetos
- `/api/v1/service-orders` — ordens de serviço
- `/api/v1/service-orders/{id}/history` — histórico da OS
- `/api/v1/dashboard` — indicadores básicos

## Testes

```bash
cd backend
pytest -q
```

Cada teste roda com o banco recriado do zero, então a suíte pode ser executada em qualquer ordem.

## Protótipo visual

O diretório `docs/` contém a interface demonstrável e está preparado para GitHub Pages. A etapa seguinte será substituir os dados fixos por dados vindos da API.

## Estratégia

1. **Fundação (2026)** — construir o Vertex Core, a identidade e o portfólio
2. **Software house** — sites, sistemas, automações e dashboards financiam o crescimento
3. **Produto** — o que se repete nos clientes vira módulo padronizado
4. **SaaS** — os melhores módulos passam a ser vendidos por assinatura
5. **Ecossistema** — Core + Flow + Data + Connect + Assistant + Compliance

> Projeto em desenvolvimento. Não use credenciais reais no ambiente demonstrativo e troque `SECRET_KEY` antes de qualquer publicação de produção.
