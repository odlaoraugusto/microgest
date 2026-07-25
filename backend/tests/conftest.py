"""
Fixtures compartilhadas dos testes.

Usa SQLite em memória para os testes rodarem rápido e sem depender de
um PostgreSQL real. Como o SQLite não suporta os tipos Enum/UUID do
Postgres da mesma forma, isso é suficiente para testar as camadas de
Service/Router; testes de integração completos devem rodar contra
Postgres (ver docs/testes.md).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.session as db_session_module
from app.db.session import Base, get_db
from app.main import app

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # O middleware de auditoria abre sua própria sessão (fora do sistema
    # de Depends do FastAPI), então precisa apontar para o mesmo banco
    # de testes - não para o Postgres real configurado em produção.
    session_local_original = db_session_module.SessionLocal
    db_session_module.SessionLocal = TestingSessionLocal

    with TestClient(app) as test_client:
        yield test_client

    db_session_module.SessionLocal = session_local_original
    app.dependency_overrides.clear()


@pytest.fixture()
def authenticated_client(client):
    """
    Mesmo TestClient da fixture `client`, mas já autenticado.

    Cria o primeiro usuário do sistema (que vira ADMIN automaticamente,
    ver UsuarioService) e anexa o token JWT como header padrão em todas
    as próximas requisições feitas com esse client - usado pelos testes
    dos módulos clínicos, que agora exigem login (ver core/deps.py).
    """
    client.post(
        "/api/usuarios",
        json={
            "nome": "Usuário de Teste",
            "email": "teste@microgest.com",
            "senha": "senha-de-teste-123",
            "perfil": "ADMIN",
        },
    )
    login = client.post(
        "/api/auth/login",
        data={"username": "teste@microgest.com", "password": "senha-de-teste-123"},
    )
    token = login.json()["data"]["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
