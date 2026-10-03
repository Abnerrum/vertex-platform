from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database.session import Base, SessionLocal, engine
from app.models.accounting_obligation import AccountingObligation  # noqa: F401
from app.models.client import Client
from app.models.project import Project
from app.models.service_order import ServiceOrder, ServiceOrderHistory
from app.models.user import User


SEED_NOTE = "Demonstração Vertex"

CLIENTS = [
    ("Aurora Café e Torrefação Ltda", "Marina Costa", "marina@auroracafe.example", "(11) 3333-4101"),
    ("Horizonte Clínica Integrada", "Rafael Nunes", "rafael@horizonteclinica.example", "(11) 3333-4102"),
    ("Vértice Materiais Elétricos", "Camila Rocha", "camila@verticemateriais.example", "(11) 3333-4103"),
    ("Casa Ipê Arquitetura", "João Martins", "joao@casaipe.example", "(11) 3333-4104"),
    ("NorteSul Logística", "Patrícia Lima", "patricia@nortesul.example", "(11) 3333-4105"),
    ("BemViva Fisioterapia", "Diego Alves", "diego@bemviva.example", "(11) 3333-4106"),
    ("Mercado Estação Central", "Fernanda Melo", "fernanda@estacaocentral.example", "(11) 3333-4107"),
    ("Oficina Rota 27", "Bruno Freitas", "bruno@rota27.example", "(11) 3333-4108"),
    ("Lume Energia Solar", "Aline Ribeiro", "aline@lumeenergia.example", "(11) 3333-4109"),
    ("Ponto Criativo Comunicação", "Lucas Barros", "lucas@pontocriativo.example", "(11) 3333-4110"),
    ("Sabor de Minas Alimentação", "Renata Dias", "renata@sabordeminas.example", "(11) 3333-4111"),
    ("Prisma Educação Profissional", "Thiago Santos", "thiago@prismaeducacao.example", "(11) 3333-4112"),
    ("Verde Campo Paisagismo", "Isabela Cardoso", "isabela@verdecampo.example", "(11) 3333-4113"),
    ("Ateliê Linha Clara", "Eduardo Pires", "eduardo@linhaclara.example", "(11) 3333-4114"),
    ("Ponte Alta Transportes", "Sofia Mendes", "sofia@pontealta.example", "(11) 3333-4115"),
]

PROJECTS = [
    (0, "Portal de pedidos B2B", "web", "development", "high", 62),
    (1, "Jornada digital do paciente", "web", "planning", "medium", 18),
    (2, "Implantação de atendimento omnichannel", "automation", "testing", "high", 88),
    (3, "Painel de acompanhamento de obras", "data", "development", "medium", 47),
    (4, "Rastreamento de entregas", "web", "testing", "urgent", 93),
    (5, "Agendamento e confirmação automática", "automation", "development", "medium", 55),
    (6, "Programa de relacionamento", "web", "planning", "low", 12),
    (8, "Monitoramento de instalações solares", "data", "development", "high", 71),
]

SERVICE_ORDERS = [
    (0, 0, "Revisar integração de pedidos", "in_progress", "high", 2),
    (1, 1, "Ajustar acesso da recepção", "open", "medium", 4),
    (2, 2, "Validar fluxo de atendimento", "waiting", "urgent", 1),
    (4, 4, "Corrigir atualização de rastreio", "assigned", "high", 3),
    (5, 5, "Configurar lembrete de sessões", "open", "low", 6),
]


def _get_or_create_client(db: Session, data: tuple[str, str, str, str]) -> tuple[Client, bool]:
    company_name, responsible_name, email, phone = data
    client = db.query(Client).filter(Client.email == email).one_or_none()
    if client:
        return client, False

    client = Client(
        company_name=company_name,
        responsible_name=responsible_name,
        email=email,
        phone=phone,
        notes=f"{SEED_NOTE}: empresa fictícia para apresentação.",
        status="active",
    )
    db.add(client)
    db.flush()
    return client, True


def _get_or_create_project(
    db: Session,
    client: Client,
    data: tuple[int, str, str, str, str, int],
    today: date,
) -> tuple[Project, bool]:
    _, name, project_type, status, priority, progress = data
    project = (
        db.query(Project)
        .filter(Project.client_id == client.id, Project.name == name)
        .one_or_none()
    )
    if project:
        return project, False

    project = Project(
        client_id=client.id,
        name=name,
        description=f"{SEED_NOTE}: projeto de exemplo para demonstrar a operação.",
        project_type=project_type,
        status=status,
        priority=priority,
        progress=progress,
        start_date=today - timedelta(days=progress // 2 + 8),
        due_date=today + timedelta(days=30 + progress // 4),
    )
    db.add(project)
    db.flush()
    return project, True


def _add_status_history(
    db: Session,
    order: ServiceOrder,
    user_id: int,
    statuses: list[str],
    created_at: datetime,
) -> int:
    existing = (
        db.query(ServiceOrderHistory)
        .filter(
            ServiceOrderHistory.service_order_id == order.id,
            ServiceOrderHistory.note.like(f"{SEED_NOTE}:%"),
        )
        .count()
    )
    if existing:
        return 0

    added = 0
    previous = None
    for index, current in enumerate(statuses):
        db.add(
            ServiceOrderHistory(
                service_order_id=order.id,
                changed_by_user_id=user_id,
                field="status",
                old_value=previous,
                new_value=current,
                note=f"{SEED_NOTE}: etapa {index + 1} da OS de exemplo.",
                created_at=created_at + timedelta(hours=index * 5),
            )
        )
        previous = current
        added += 1
    return added


def seed_demo(db: Session) -> dict[str, int]:
    """Insere dados fictícios sem duplicar registros já semeados."""
    user = db.query(User).filter(User.is_active.is_(True)).order_by(User.id).first()
    if not user:
        raise RuntimeError("Crie o primeiro administrador pela tela de login antes de semear os dados.")

    today = date.today()
    clients_by_email: dict[str, Client] = {}
    created = {"clients": 0, "projects": 0, "service_orders": 0, "audit_events": 0}

    for data in CLIENTS:
        client, was_created = _get_or_create_client(db, data)
        clients_by_email[data[2]] = client
        created["clients"] += int(was_created)

    clients = [clients_by_email[data[2]] for data in CLIENTS]
    projects_by_index: dict[int, Project] = {}
    for data in PROJECTS:
        project, was_created = _get_or_create_project(db, clients[data[0]], data, today)
        projects_by_index[data[0]] = project
        created["projects"] += int(was_created)

    for index, project_index, title, status, priority, due_in_days in SERVICE_ORDERS:
        code = f"DEMO-OS-{index + 1:03d}"
        order = db.query(ServiceOrder).filter(ServiceOrder.code == code).one_or_none()
        if order:
            continue

        created_at = datetime.now(timezone.utc) - timedelta(days=4 + index)
        status_paths = {
            "open": ["open"],
            "assigned": ["open", "assigned"],
            "in_progress": ["open", "assigned", "in_progress"],
            "waiting": ["open", "assigned", "in_progress", "waiting"],
        }
        order = ServiceOrder(
            code=code,
            client_id=clients[index].id,
            project_id=projects_by_index[project_index].id,
            assigned_user_id=user.id if status != "open" else None,
            created_by_user_id=user.id,
            title=title,
            description=f"{SEED_NOTE}: solicitação fictícia para demonstração do fluxo de OS.",
            priority=priority,
            status=status,
            due_date=today + timedelta(days=due_in_days),
            created_at=created_at,
            updated_at=created_at + timedelta(days=1),
        )
        db.add(order)
        db.flush()
        created["service_orders"] += 1
        created["audit_events"] += _add_status_history(
            db,
            order,
            user.id,
            status_paths[status],
            created_at,
        )

    db.commit()
    return created


def main() -> None:
    """Prepara as tabelas e executa o seed no banco configurado."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        totals = seed_demo(db)
        print("Dados demonstrativos prontos:")
        for entity, count in totals.items():
            print(f"- {entity}: {count} novo(s)")
        print("O seed pode ser executado novamente sem duplicar os exemplos.")
    except RuntimeError as error:
        db.rollback()
        raise SystemExit(str(error)) from error
    finally:
        db.close()


if __name__ == "__main__":
    main()