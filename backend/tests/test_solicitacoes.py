"""
Testes do módulo Solicitações (Sprint 5).
"""
import pytest


def _criar_paciente(authenticated_client, prontuario="999"):
    resp = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Teste", "prontuario": prontuario}
    )
    return resp.json()["data"]


def test_criar_solicitacao_com_sucesso(authenticated_client):
    paciente = _criar_paciente(authenticated_client)

    response = authenticated_client.post(
        "/api/solicitacoes",
        json={
            "paciente_id": paciente["id"],
            "material": "Hemocultura",
            "origem": "UTI",
            "prioridade": "URGENTE",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["material"] == "Hemocultura"
    assert body["data"]["status"] == "AGUARDANDO_COLETA"
    assert body["data"]["paciente"]["nome"] == "Paciente Teste"


def test_nao_permite_solicitacao_para_paciente_inexistente(authenticated_client):
    response = authenticated_client.post(
        "/api/solicitacoes",
        json={
            "paciente_id": "00000000-0000-0000-0000-000000000000",
            "material": "Urina",
        },
    )

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_listar_solicitacoes_filtra_por_paciente(authenticated_client):
    paciente_1 = _criar_paciente(authenticated_client, "111")
    paciente_2 = _criar_paciente(authenticated_client, "222")

    authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente_1["id"], "material": "Urina"}
    )
    authenticated_client.post(
        "/api/solicitacoes",
        json={"paciente_id": paciente_2["id"], "material": "Sangue"},
    )

    response = authenticated_client.get("/api/solicitacoes", params={"paciente_id": paciente_1["id"]})

    body = response.json()
    assert body["data"]["total"] == 1
    assert body["data"]["items"][0]["material"] == "Urina"


def test_atualizar_status_para_coletado_marca_data_coleta(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criada = authenticated_client.post(
        "/api/solicitacoes",
        json={"paciente_id": paciente["id"], "material": "Escarro"},
    ).json()["data"]

    response = authenticated_client.put(
        f"/api/solicitacoes/{criada['id']}", json={"status": "COLETADO"}
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["status"] == "COLETADO"
    assert body["data_coleta"] is not None


def test_nao_permite_alterar_status_de_solicitacao_liberada(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criada = authenticated_client.post(
        "/api/solicitacoes",
        json={"paciente_id": paciente["id"], "material": "Líquor"},
    ).json()["data"]

    authenticated_client.put(f"/api/solicitacoes/{criada['id']}", json={"status": "LIBERADO"})

    response = authenticated_client.put(
        f"/api/solicitacoes/{criada['id']}", json={"status": "EM_ANALISE"}
    )

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_remover_solicitacao_soft_delete(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criada = authenticated_client.post(
        "/api/solicitacoes",
        json={"paciente_id": paciente["id"], "material": "Fezes"},
    ).json()["data"]

    response = authenticated_client.delete(f"/api/solicitacoes/{criada['id']}")
    assert response.status_code == 200

    consulta = authenticated_client.get(f"/api/solicitacoes/{criada['id']}")
    assert consulta.status_code == 404
