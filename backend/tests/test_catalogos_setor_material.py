"""
Testes dos catálogos de Setores e Materiais (Sprint 11).
"""


def test_criar_setor_com_sucesso(authenticated_client):
    response = authenticated_client.post("/api/setores", json={"nome": "UTI Pediátrica"})
    assert response.status_code == 201
    assert response.json()["data"]["nome"] == "UTI Pediátrica"


def test_nao_permite_setor_duplicado(authenticated_client):
    authenticated_client.post("/api/setores", json={"nome": "Enfermaria"})
    response = authenticated_client.post("/api/setores", json={"nome": "Enfermaria"})
    assert response.status_code == 422


def test_listar_setores(authenticated_client):
    authenticated_client.post("/api/setores", json={"nome": "Centro Cirúrgico"})
    response = authenticated_client.get("/api/setores")
    assert response.status_code == 200
    nomes = [s["nome"] for s in response.json()["data"]["items"]]
    assert "Centro Cirúrgico" in nomes


def test_atualizar_setor(authenticated_client):
    criado = authenticated_client.post("/api/setores", json={"nome": "Ambulatorio"}).json()["data"]
    response = authenticated_client.put(
        f"/api/setores/{criado['id']}", json={"nome": "Ambulatório"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["nome"] == "Ambulatório"


def test_remover_setor(authenticated_client):
    criado = authenticated_client.post("/api/setores", json={"nome": "Setor Temporário"}).json()["data"]
    response = authenticated_client.delete(f"/api/setores/{criado['id']}")
    assert response.status_code == 200


def test_setores_exigem_autenticacao(client):
    response = client.get("/api/setores")
    assert response.status_code == 401


def test_criar_material_com_sucesso(authenticated_client):
    response = authenticated_client.post("/api/materiais", json={"nome": "Lavado Broncoalveolar"})
    assert response.status_code == 201
    assert response.json()["data"]["nome"] == "Lavado Broncoalveolar"


def test_nao_permite_material_duplicado(authenticated_client):
    authenticated_client.post("/api/materiais", json={"nome": "Urina"})
    response = authenticated_client.post("/api/materiais", json={"nome": "Urina"})
    assert response.status_code == 422


def test_listar_materiais(authenticated_client):
    authenticated_client.post("/api/materiais", json={"nome": "Ponta de Cateter"})
    response = authenticated_client.get("/api/materiais")
    assert response.status_code == 200
    nomes = [m["nome"] for m in response.json()["data"]["items"]]
    assert "Ponta de Cateter" in nomes


def test_materiais_exigem_autenticacao(client):
    response = client.get("/api/materiais")
    assert response.status_code == 401
