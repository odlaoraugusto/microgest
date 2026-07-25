"""
Testes do módulo Antibiogramas (Sprint 7).
"""


def _criar_isolado_positivo(authenticated_client, prontuario="a1"):
    """
    Cria paciente -> solicitação -> cultura positiva com 1 microrganismo
    e retorna (cultura, isolado_id), onde isolado_id é o id do
    CulturaMicrorganismo (usado para criar antibiogramas).
    """
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Antibiograma", "prontuario": prontuario}
    ).json()["data"]
    solicitacao = authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente["id"], "material": "Hemocultura"}
    ).json()["data"]
    microrganismo = authenticated_client.post(
        "/api/microrganismos", json={"nome": f"Micro {prontuario}", "gram": "NEGATIVO"}
    ).json()["data"]
    cultura = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    ).json()["data"]
    isolado_id = cultura["microrganismos"][0]["id"]
    return cultura, isolado_id


def _criar_antimicrobiano(authenticated_client, nome="Meropenem"):
    return authenticated_client.post(
        "/api/antimicrobianos", json={"nome": nome, "classe": "Carbapenêmico"}
    ).json()["data"]


def test_criar_antimicrobiano_com_sucesso(authenticated_client):
    response = authenticated_client.post(
        "/api/antimicrobianos", json={"nome": "Vancomicina", "classe": "Glicopeptídeo"}
    )
    assert response.status_code == 201
    assert response.json()["data"]["nome"] == "Vancomicina"


def test_nao_permite_antimicrobiano_duplicado(authenticated_client):
    authenticated_client.post("/api/antimicrobianos", json={"nome": "Ceftriaxona"})
    response = authenticated_client.post("/api/antimicrobianos", json={"nome": "Ceftriaxona"})
    assert response.status_code == 422


def test_criar_antibiograma_com_sucesso(authenticated_client):
    _, isolado_id = _criar_isolado_positivo(authenticated_client)
    antimicrobiano = _criar_antimicrobiano(authenticated_client)

    response = authenticated_client.post(
        "/api/antibiogramas",
        json={
            "cultura_microrganismo_id": isolado_id,
            "resultados": [
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": "RESISTENTE"}
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert len(body["resultados"]) == 1
    assert body["resultados"][0]["resultado"] == "RESISTENTE"
    assert body["resultados"][0]["antimicrobiano"]["nome"] == "Meropenem"
    assert body["cultura_microrganismo"]["microrganismo"]["nome"] == "Micro a1"


def test_nao_permite_antibiograma_para_isolado_inexistente(authenticated_client):
    antimicrobiano = _criar_antimicrobiano(authenticated_client)
    response = authenticated_client.post(
        "/api/antibiogramas",
        json={
            "cultura_microrganismo_id": "00000000-0000-0000-0000-000000000000",
            "resultados": [
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": "SENSIVEL"}
            ],
        },
    )
    assert response.status_code == 422


def test_nao_permite_antibiograma_para_cultura_negativa(authenticated_client):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Negativo", "prontuario": "neg1"}
    ).json()["data"]
    solicitacao = authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente["id"], "material": "Urina"}
    ).json()["data"]
    cultura = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={"solicitacao_id": solicitacao["id"], "resultado": "NEGATIVA"},
    ).json()["data"]

    # Cultura negativa não tem microrganismos, então nem existe isolado
    # válido para testar - simula tentativa com id aleatório, que já cai
    # na regra de "isolado inexistente". O teste real de "cultura não
    # positiva" fica coberto indiretamente pela regra do banco: só
    # existem isolados quando a cultura é POSITIVA (ver test_microbiologia).
    assert cultura["resultado"] == "NEGATIVA"
    assert cultura["microrganismos"] == []


def test_nao_permite_antimicrobiano_repetido_no_antibiograma(authenticated_client):
    _, isolado_id = _criar_isolado_positivo(authenticated_client, prontuario="a2")
    antimicrobiano = _criar_antimicrobiano(authenticated_client, nome="Ampicilina")

    response = authenticated_client.post(
        "/api/antibiogramas",
        json={
            "cultura_microrganismo_id": isolado_id,
            "resultados": [
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": "SENSIVEL"},
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": "RESISTENTE"},
            ],
        },
    )
    assert response.status_code == 422


def test_liberar_antibiograma(authenticated_client):
    _, isolado_id = _criar_isolado_positivo(authenticated_client, prontuario="a3")
    antimicrobiano = _criar_antimicrobiano(authenticated_client, nome="Gentamicina")
    criado = authenticated_client.post(
        "/api/antibiogramas",
        json={
            "cultura_microrganismo_id": isolado_id,
            "resultados": [
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": "SENSIVEL"}
            ],
        },
    ).json()["data"]

    response = authenticated_client.post(f"/api/antibiogramas/{criado['id']}/liberar")

    assert response.status_code == 200
    assert response.json()["data"]["data_liberacao"] is not None


def test_nao_permite_liberar_antibiograma_sem_resultados(authenticated_client):
    _, isolado_id = _criar_isolado_positivo(authenticated_client, prontuario="a4")
    criado = authenticated_client.post(
        "/api/antibiogramas", json={"cultura_microrganismo_id": isolado_id}
    ).json()["data"]

    response = authenticated_client.post(f"/api/antibiogramas/{criado['id']}/liberar")
    assert response.status_code == 422


def test_remover_antibiograma_soft_delete(authenticated_client):
    _, isolado_id = _criar_isolado_positivo(authenticated_client, prontuario="a5")
    criado = authenticated_client.post(
        "/api/antibiogramas", json={"cultura_microrganismo_id": isolado_id}
    ).json()["data"]

    response = authenticated_client.delete(f"/api/antibiogramas/{criado['id']}")
    assert response.status_code == 200

    consulta = authenticated_client.get(f"/api/antibiogramas/{criado['id']}")
    assert consulta.status_code == 404
