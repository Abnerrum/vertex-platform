# Vertex Platform

Plataforma de gestão da **Vertex Tech Solutions**.

## Fase 1
MVP para administrar clientes, projetos, ordens de serviço e indicadores.

### Stack planejada
- Frontend: React (e protótipo navegável estático nesta primeira entrega)
- Backend: Python + FastAPI
- Banco: PostgreSQL
- ORM: SQLAlchemy
- Testes: Pytest
- Containers: Docker

## Fluxo principal
Login → Dashboard → Clientes → Projetos → Serviços/OS → Histórico

## Executar API
```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000/docs`.

## Protótipo visual
O diretório `docs/` contém a primeira interface demonstrável e está preparado para GitHub Pages.

> Projeto em desenvolvimento. Não use dados pessoais ou credenciais reais no protótipo.
