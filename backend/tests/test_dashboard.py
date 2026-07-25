"""
Testes do módulo Dashboard (Sprint 8).
"""


def _get_or_criar_microrganismo(authenticated_client, nome):
    """
    Cria o microrganismo, ou reaproveita o já existente se o nome já
    tiver sido usado em outra chamada dentro do mesmo teste (a API
    corretamente rejeita nomes duplicados com 422).
    """
    resposta = authenticated_client.post("/api/microrganismos", json={"nome": nome})
    if resposta.status_code == 201:
        return resposta.json()["data"]

    existentes = authenticated_client.get("/api/microrganismos", params={"termo": nome}).json()["data"]["items"]
    return next(m for m in existentes if m["nome"] == nome)


def _fluxo_completo(authenticated_client, prontuario, resultado="POSITIVA", nome_micro="Micro X"):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Dash", "prontuario": prontuario}
    ).json()["data"]
    solicitacao = authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente["id"], "material": "Urina"}
    ).json()["data"]

    payload = {"solicitacao_id": solicitacao["id"], "resultado": resultado}
    if resultado == "POSITIVA":
        micro = _get_or_criar_microrganismo(authenticated_client, nome_micro)
        payload["microrganismo_ids"] = [micro["id"]]

    cultura = authenticated_client.post("/api/microbiologia/culturas", json=payload).json()["data"]
    return paciente, solicitacao, cultura


def test_resumo_dashboard_estrutura_basica(authenticated_client):
    response = authenticated_client.get("/api/dashboard/resumo")
    assert response.status_code == 200
    body = response.json()["data"]
    for campo in (
        "culturas_hoje",
        "aguardando_atualizacao",
        "prazo_vencido",
        "liberados_hoje",
        "top_microrganismos",
        "alertas",
    ):
        assert campo in body


def test_culturas_hoje_conta_culturas_criadas(authenticated_client):
    _fluxo_completo(authenticated_client, "d1", resultado="NEGATIVA")
    _fluxo_completo(authenticated_client, "d2", resultado="NEGATIVA")

    body = authenticated_client.get("/api/dashboard/resumo").json()["data"]
    assert body["culturas_hoje"] == 2


def test_aguardando_atualizacao_conta_solicitacoes_em_andamento(authenticated_client):
    _fluxo_completo(authenticated_client, "d3", resultado="NEGATIVA")

    body = authenticated_client.get("/api/dashboard/resumo").json()["data"]
    # a solicitação criada continua em AGUARDANDO_COLETA (status não mexido)
    assert body["aguardando_atualizacao"] >= 1


def test_liberados_hoje_conta_culturas_liberadas(authenticated_client):
    _, _, cultura = _fluxo_completo(authenticated_client, "d4", resultado="NEGATIVA")
    authenticated_client.post(f"/api/microbiologia/culturas/{cultura['id']}/liberar")

    body = authenticated_client.get("/api/dashboard/resumo").json()["data"]
    assert body["liberados_hoje"] == 1


def test_top_microrganismos_reflete_culturas_positivas(authenticated_client):
    _fluxo_completo(authenticated_client, "d5", resultado="POSITIVA", nome_micro="Klebsiella pneumoniae")
    _fluxo_completo(authenticated_client, "d6", resultado="POSITIVA", nome_micro="Klebsiella pneumoniae")

    body = authenticated_client.get("/api/dashboard/resumo").json()["data"]
    nomes = [m["nome"] for m in body["top_microrganismos"]]
    assert "Klebsiella pneumoniae" in nomes


def test_alerta_de_cultura_positiva_aguardando_liberacao(authenticated_client):
    _fluxo_completo(authenticated_client, "d7", resultado="POSITIVA", nome_micro="Acinetobacter baumannii")

    body = authenticated_client.get("/api/dashboard/resumo").json()["data"]
    tipos = [a["tipo"] for a in body["alertas"]]
    assert "info" in tipos
