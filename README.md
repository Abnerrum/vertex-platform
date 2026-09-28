# Vertex Platform

Plataforma de gestão empresarial em desenvolvimento. **Vertex** continua como nome provisório até a definição da marca definitiva.

## Fase 1
MVP para administrar usuários, clientes, projetos, ordens de serviço e indicadores.

### Stack
- Frontend: protótipo estático agora; React na integração
- Backend: Python + FastAPI
- Banco: PostgreSQL (SQLite disponível para desenvolvimento)
- ORM: SQLAlchemy
- Autenticação: JWT + perfis de acesso
- Testes: Pytest
- Containers: Docker

## Status atual — v0.3.0
- API FastAPI
- Docker/PostgreSQL
- Modelo de usuários e clientes
- Primeiro administrador via bootstrap
- Login JWT
- Perfis: admin, comercial, técnico e financeiro
- CRUD de clientes protegido por autenticação
- Testes de saúde, login e clientes

## Fluxo principal
Login → Dashboard → Clientes → Projetos → Serviços/OS → Histórico

## Executar API
```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

No Windows, copie manualmente `.env.example` para `.env` caso o comando `cp` não esteja disponível.

A documentação interativa fica em `http://127.0.0.1:8000/docs`.

## Criar o primeiro administrador
Com o banco vazio, use uma única vez:

```http
POST /api/v1/auth/bootstrap
```

Exemplo de corpo:

```json
{
  "name": "Administrador",
  "email": "admin@example.com",
  "password": "troque-por-uma-senha-forte"
}
```

Depois, faça login em `POST /api/v1/auth/login`. As rotas de clientes exigem o token Bearer retornado pelo login.

## Testes
```bash
cd backend
pytest -q
```

## Protótipo visual
O diretório `docs/` contém a interface demonstrável e está preparado para GitHub Pages.

> Projeto em desenvolvimento. Não use credenciais reais no ambiente demonstrativo e troque `SECRET_KEY` antes de qualquer publicação de produção.
