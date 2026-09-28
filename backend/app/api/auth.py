from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    BootstrapAdmin,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido ou inativo",
        )
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao administrador",
        )
    return current_user

@router.post(
    "/bootstrap",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def bootstrap_admin(payload: BootstrapAdmin, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Administrador inicial já configurado",
        )

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        user=user,
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        user=user,
    )

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id).all()

@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
