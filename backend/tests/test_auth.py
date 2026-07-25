"""
Testes do módulo de Autenticação e Usuários (Sprint 12).
"""


def _criar_primeiro_usuario(client, email="admin@microgest.com", senha="senha12345"):
    """O primeiro usuário do sistema é sempre promovido a ADMIN."""
    return client.post(
        "/api/usuarios",
        json={"nome": "Admin", "email": email, "senha": senha, "perfil": "VISUALIZADOR"},
    ).json()["data"]


def _login(client, email="admin@microgest.com", senha="senha12345"):
    response = client.post(
        "/api/auth/login", data={"username": email, "password": senha}
    )
    return response.json()["data"]["access_token"]


def test_primeiro_usuario_criado_sem_auth_vira_admin(client):
    usuario = _criar_primeiro_usuario(client)
    assert usuario["perfil"] == "ADMIN"


def test_criar_segundo_usuario_sem_token_falha(client):
    _criar_primeiro_usuario(client)

    response = client.post(
        "/api/usuarios",
        json={
            "nome": "Técnico",
            "email": "tecnico@microgest.com",
            "senha": "outrasenha123",
            "perfil": "TECNICO",
        },
    )
    assert response.status_code == 401


def test_criar_segundo_usuario_com_admin_funciona(client):
    _criar_primeiro_usuario(client)
    token = _login(client)

    response = client.post(
        "/api/usuarios",
        json={
            "nome": "Técnico",
            "email": "tecnico@microgest.com",
            "senha": "outrasenha123",
            "perfil": "TECNICO",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["data"]["perfil"] == "TECNICO"


def test_login_com_senha_errada_falha(client):
    _criar_primeiro_usuario(client)

    response = client.post(
        "/api/auth/login", data={"username": "admin@microgest.com", "password": "senha_errada"}
    )
    assert response.status_code == 401


def test_login_com_sucesso_retorna_token(client):
    _criar_primeiro_usuario(client)
    token = _login(client)
    assert isinstance(token, str) and len(token) > 10


def test_me_retorna_usuario_autenticado(client):
    _criar_primeiro_usuario(client)
    token = _login(client)

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["data"]["email"] == "admin@microgest.com"


def test_me_sem_token_falha(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_listar_usuarios_exige_admin(client):
    _criar_primeiro_usuario(client)
    token_admin = _login(client)
    client.post(
        "/api/usuarios",
        json={
            "nome": "Visualizador",
            "email": "visu@microgest.com",
            "senha": "senhavisu123",
            "perfil": "VISUALIZADOR",
        },
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    token_visualizador = _login(client, email="visu@microgest.com", senha="senhavisu123")

    response_admin = client.get(
        "/api/usuarios", headers={"Authorization": f"Bearer {token_admin}"}
    )
    response_visualizador = client.get(
        "/api/usuarios", headers={"Authorization": f"Bearer {token_visualizador}"}
    )

    assert response_admin.status_code == 200
    assert response_admin.json()["data"]["total"] == 2
    assert response_visualizador.status_code == 403


def test_nao_permite_email_duplicado(client):
    _criar_primeiro_usuario(client)
    token = _login(client)

    response = client.post(
        "/api/usuarios",
        json={
            "nome": "Duplicado",
            "email": "admin@microgest.com",
            "senha": "outrasenha123",
            "perfil": "TECNICO",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
