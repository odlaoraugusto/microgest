"""
Testes do módulo Exames.

O módulo Exames compõe Solicitação + Cultura numa única operação: uma
solicitação já nasce COLETADA (sem a etapa manual de editar status), e a
cultura é criada junto, na mesma chamada. Os módulos Solicitações e
Microbiologia continuam funcionando de forma independente (ver
test_solicitacoes.py e test_microbiologia.py) - este arquivo cobre
apenas a camada nova.
"""


def _criar_paciente(authenticated_client, prontuario="p1"):
    return authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Exame", "prontuario": prontuario}
    ).json()["data"]


def _criar_microrganismo(authenticated_client, nome="Klebsiella pneumoniae"):
    return authenticated_client.post(
        "/api/microrganismos",
        json={"nome": nome, "gram": "NEGATIVO", "tipo": "BACTERIA"},
    ).json()["data"]


def _criar_exame(authenticated_client, paciente_id=None, prontuario="p1", nome="Paciente Exame", **extra):
    """
    `paciente_id` é aceito só por compatibilidade com os testes que já
    tinham um paciente pronto - o campo em si não existe mais no payload,
    o exame sempre lança por prontuário+nome (paciente automático).
    """
    payload = {
        "paciente_prontuario": prontuario,
        "paciente_nome": nome,
        "material": "Hemocultura",
        **extra,
    }
    return authenticated_client.post("/api/exames", json=payload)


def test_criar_exame_com_sucesso(authenticated_client):
    response = _criar_exame(authenticated_client, resultado="NEGATIVA")

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["solicitacao"]["status"] == "COLETADO"
    assert body["solicitacao"]["data_coleta"] is not None
    assert body["solicitacao"]["material"] == "Hemocultura"
    assert body["resultado"] == "NEGATIVA"


def test_criar_exame_cria_paciente_automaticamente_por_prontuario(authenticated_client):
    response = _criar_exame(
        authenticated_client, prontuario="novo-123", nome="Fulano de Tal"
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["solicitacao"]["paciente"]["prontuario"] == "novo-123"
    assert body["solicitacao"]["paciente"]["nome"] == "Fulano de Tal"

    # o paciente realmente foi criado (não é só um campo solto na resposta)
    listagem = authenticated_client.get("/api/pacientes?termo=novo-123").json()["data"]
    assert listagem["total"] == 1


def test_criar_exame_reaproveita_paciente_existente_sem_sobrescrever_nome(
    authenticated_client,
):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Nome Original", "prontuario": "p-existente"}
    ).json()["data"]

    response = _criar_exame(
        authenticated_client, prontuario="p-existente", nome="Nome Digitado Errado"
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["solicitacao"]["paciente"]["id"] == paciente["id"]
    assert body["solicitacao"]["paciente"]["nome"] == "Nome Original"

    listagem = authenticated_client.get("/api/pacientes?termo=p-existente").json()["data"]
    assert listagem["total"] == 1


def test_nao_permite_exame_sem_prontuario(authenticated_client):
    response = authenticated_client.post(
        "/api/exames",
        json={"paciente_nome": "Fulano", "material": "Hemocultura"},
    )

    assert response.status_code == 422


def test_criar_exame_positivo_com_microrganismo(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    microrganismo = _criar_microrganismo(authenticated_client)

    response = _criar_exame(
        authenticated_client,
        paciente["id"],
        resultado="POSITIVA",
        microrganismo_ids=[microrganismo["id"]],
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["resultado"] == "POSITIVA"
    assert len(body["microrganismos"]) == 1
    assert body["microrganismos"][0]["microrganismo"]["nome"] == "Klebsiella pneumoniae"


def test_nao_permite_microrganismo_em_exame_nao_positivo(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    microrganismo = _criar_microrganismo(authenticated_client)

    response = _criar_exame(
        authenticated_client,
        paciente["id"],
        resultado="NEGATIVA",
        microrganismo_ids=[microrganismo["id"]],
    )

    assert response.status_code == 422


def test_listar_exames(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    _criar_exame(authenticated_client, paciente["id"], resultado="NEGATIVA")
    _criar_exame(authenticated_client, paciente["id"], resultado="EM_ANALISE")

    response = authenticated_client.get("/api/exames")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_obter_exame_especifico(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criado = _criar_exame(authenticated_client, paciente["id"]).json()["data"]

    response = authenticated_client.get(f"/api/exames/{criado['id']}")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == criado["id"]


def test_atualizar_exame_so_resultado_nao_altera_solicitacao(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criado = _criar_exame(authenticated_client, paciente["id"]).json()["data"]

    response = authenticated_client.put(
        f"/api/exames/{criado['id']}", json={"resultado": "NEGATIVA"}
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["resultado"] == "NEGATIVA"
    assert body["solicitacao"]["material"] == "Hemocultura"


def test_atualizar_exame_so_material_nao_altera_cultura(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criado = _criar_exame(authenticated_client, paciente["id"], resultado="NEGATIVA").json()[
        "data"
    ]

    response = authenticated_client.put(
        f"/api/exames/{criado['id']}", json={"material": "Urina"}
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["solicitacao"]["material"] == "Urina"
    assert body["resultado"] == "NEGATIVA"


def test_liberar_exame(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criado = _criar_exame(authenticated_client, paciente["id"], resultado="NEGATIVA").json()[
        "data"
    ]

    response = authenticated_client.post(f"/api/exames/{criado['id']}/liberar")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["liberado_tecnicamente"] is True


def test_remover_exame(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    criado = _criar_exame(authenticated_client, paciente["id"]).json()["data"]

    delete_response = authenticated_client.delete(f"/api/exames/{criado['id']}")
    get_response = authenticated_client.get(f"/api/exames/{criado['id']}")

    assert delete_response.status_code == 200
    assert get_response.status_code == 404
