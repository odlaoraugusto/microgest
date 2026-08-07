"""
Testes do módulo Microbiologia (Sprint 6).
"""


def _criar_paciente(authenticated_client, prontuario="p1"):
    return authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Cultura", "prontuario": prontuario}
    ).json()["data"]


def _criar_solicitacao(authenticated_client, paciente_id, material="Hemocultura"):
    return authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente_id, "material": material}
    ).json()["data"]


def _criar_microrganismo(authenticated_client, nome="Klebsiella pneumoniae"):
    return authenticated_client.post(
        "/api/microrganismos",
        json={"nome": nome, "gram": "NEGATIVO", "tipo": "BACTERIA"},
    ).json()["data"]


def test_criar_microrganismo_com_sucesso(authenticated_client):
    response = authenticated_client.post(
        "/api/microrganismos",
        json={"nome": "Escherichia coli", "gram": "NEGATIVO", "tipo": "BACTERIA"},
    )
    assert response.status_code == 201
    assert response.json()["data"]["nome"] == "Escherichia coli"


def test_nao_permite_microrganismo_duplicado(authenticated_client):
    authenticated_client.post("/api/microrganismos", json={"nome": "Candida albicans"})
    response = authenticated_client.post("/api/microrganismos", json={"nome": "Candida albicans"})
    assert response.status_code == 422


def test_microrganismo_seedado_com_taxonomia_correta(authenticated_client):
    """
    Confere que os campos novos de taxonomia (gram/tipo/morfologia/
    fermentador/familia) trafegam corretamente do cadastro até o GET.

    O banco de testes é montado a partir do metadata do SQLAlchemy (ver
    conftest.py), não roda a migração 0012 - então aqui reproduzimos os
    mesmos valores que a migração grava em produção pra "Klebsiella
    pneumoniae" e conferimos o roundtrip. A aplicação real da migração
    contra o Postgres do Supabase é validada separadamente (consulta
    manual pós-upgrade).
    """
    criado = authenticated_client.post(
        "/api/microrganismos",
        json={
            "nome": "Klebsiella pneumoniae",
            "gram": "NEGATIVO",
            "tipo": "BACTERIA",
            "morfologia": "BACILO",
            "fermentador": True,
            "familia": "Enterobacteriaceae",
        },
    ).json()["data"]

    response = authenticated_client.get("/api/microrganismos", params={"termo": "Klebsiella"})

    assert response.status_code == 200
    item = next(i for i in response.json()["data"]["items"] if i["id"] == criado["id"])
    assert item["gram"] == "NEGATIVO"
    assert item["morfologia"] == "BACILO"
    assert item["fermentador"] is True
    assert item["familia"] == "Enterobacteriaceae"


def test_novo_microrganismo_herda_taxonomia_do_mesmo_genero(authenticated_client):
    """
    "Aprendizado" incremental da base de conhecimento: cadastrar uma nova
    espécie de um gênero já conhecido (sem informar taxonomia) herda
    gram/tipo/morfologia/fermentador/familia do primeiro microrganismo
    ativo desse gênero, em vez de cair nos defaults genéricos.
    """
    authenticated_client.post(
        "/api/microrganismos",
        json={
            "nome": "Klebsiella pneumoniae",
            "gram": "NEGATIVO",
            "tipo": "BACTERIA",
            "morfologia": "BACILO",
            "fermentador": True,
            "familia": "Enterobacteriaceae",
        },
    )

    response = authenticated_client.post(
        "/api/microrganismos", json={"nome": "Klebsiella aerogenes"}
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["gram"] == "NEGATIVO"
    assert body["tipo"] == "BACTERIA"
    assert body["morfologia"] == "BACILO"
    assert body["fermentador"] is True
    assert body["familia"] == "Enterobacteriaceae"


def test_criar_microrganismo_com_campos_explicitos_nao_e_sobrescrito_pela_heranca(
    authenticated_client,
):
    """
    Se o cliente informar a taxonomia explicitamente na criação, a
    herança automática por gênero é pulada - o que foi enviado prevalece,
    mesmo já existindo outro microrganismo do mesmo gênero cadastrado.
    """
    authenticated_client.post(
        "/api/microrganismos",
        json={
            "nome": "Klebsiella pneumoniae",
            "gram": "NEGATIVO",
            "tipo": "BACTERIA",
            "morfologia": "BACILO",
            "fermentador": True,
            "familia": "Enterobacteriaceae",
        },
    )

    response = authenticated_client.post(
        "/api/microrganismos",
        json={
            "nome": "Klebsiella oxytoca",
            "gram": "POSITIVO",
            "morfologia": "COCO",
            "fermentador": False,
            "familia": "Familia Diferente",
        },
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["gram"] == "POSITIVO"
    assert body["morfologia"] == "COCO"
    assert body["fermentador"] is False
    assert body["familia"] == "Familia Diferente"


def test_criar_cultura_em_analise(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])

    response = authenticated_client.post(
        "/api/microbiologia/culturas", json={"solicitacao_id": solicitacao["id"]}
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["resultado"] == "EM_ANALISE"
    assert body["solicitacao"]["material"] == "Hemocultura"


def test_nao_permite_cultura_para_solicitacao_inexistente(authenticated_client):
    response = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={"solicitacao_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 422


def test_nao_permite_microrganismo_em_cultura_negativa(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)

    response = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "NEGATIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    )

    assert response.status_code == 422


def test_cultura_positiva_com_microrganismo(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)

    response = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    )

    assert response.status_code == 201
    body = response.json()["data"]
    assert body["resultado"] == "POSITIVA"
    assert len(body["microrganismos"]) == 1
    assert body["microrganismos"][0]["microrganismo"]["nome"] == "Klebsiella pneumoniae"


def test_liberar_cultura(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={"solicitacao_id": solicitacao["id"], "resultado": "NEGATIVA"},
    ).json()["data"]

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["liberado_tecnicamente"] is True
    assert body["data_liberacao"] is not None


def test_nao_permite_liberar_cultura_em_analise(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    criada = authenticated_client.post(
        "/api/microbiologia/culturas", json={"solicitacao_id": solicitacao["id"]}
    ).json()["data"]

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 422


def test_nao_permite_liberar_cultura_duas_vezes(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={"solicitacao_id": solicitacao["id"], "resultado": "NEGATIVA"},
    ).json()["data"]

    authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")
    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 422


def test_previsao_liberacao_e_calculada_automaticamente(authenticated_client):
    from datetime import date, timedelta

    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])

    criada = authenticated_client.post(
        "/api/microbiologia/culturas", json={"solicitacao_id": solicitacao["id"]}
    ).json()["data"]

    # Sem o parâmetro "prazo_solicitacao_dias" seedado (banco de teste usa
    # apenas o metadata, não a migração), o fallback do service é 2 dias.
    esperado = (date.today() + timedelta(days=2)).isoformat()
    assert criada["previsao_liberacao"] == esperado


def test_previsao_liberacao_pode_ser_informada_manualmente(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])

    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={"solicitacao_id": solicitacao["id"], "previsao_liberacao": "2026-12-25"},
    ).json()["data"]

    assert criada["previsao_liberacao"] == "2026-12-25"


def test_nao_permite_liberar_cultura_positiva_sem_microrganismo(authenticated_client):
    # Caso de borda: resultado POSITIVA definido via update, sem nenhum
    # microrganismo vinculado ainda.
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    criada = authenticated_client.post(
        "/api/microbiologia/culturas", json={"solicitacao_id": solicitacao["id"]}
    ).json()["data"]

    microrganismo = _criar_microrganismo(authenticated_client)
    authenticated_client.put(
        f"/api/microbiologia/culturas/{criada['id']}",
        json={"resultado": "POSITIVA", "microrganismo_ids": [microrganismo["id"]]},
    )
    # remove o microrganismo de novo, simulando cultura positiva sem isolado
    authenticated_client.put(
        f"/api/microbiologia/culturas/{criada['id']}",
        json={"microrganismo_ids": []},
    )

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 422
    assert "microrganismo" in response.json()["message"].lower()


def test_nao_permite_liberar_cultura_positiva_sem_antibiograma(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    ).json()["data"]

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 422
    assert "antibiograma" in response.json()["message"].lower()


def test_permite_liberar_cultura_positiva_com_antibiograma_completo(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    ).json()["data"]
    isolado_id = criada["microrganismos"][0]["id"]

    antimicrobiano = authenticated_client.post(
        "/api/antimicrobianos", json={"nome": "Meropenem"}
    ).json()["data"]
    authenticated_client.post(
        "/api/antibiogramas",
        json={
            "cultura_microrganismo_id": isolado_id,
            "resultados": [
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": "SENSIVEL"}
            ],
        },
    )

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 200
    assert response.json()["data"]["liberado_tecnicamente"] is True


def test_resultados_parciais_lista_culturas_em_andamento(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao_1 = _criar_solicitacao(authenticated_client, paciente["id"], material="Hemocultura")
    solicitacao_2 = _criar_solicitacao(authenticated_client, paciente["id"], material="Urina")

    # Cultura 1: em análise (ainda sem resultado)
    authenticated_client.post("/api/microbiologia/culturas", json={"solicitacao_id": solicitacao_1["id"]})

    # Cultura 2: positiva, já liberada (não deve aparecer nos parciais)
    micro = _criar_microrganismo(authenticated_client, nome="Escherichia coli")
    cultura_2 = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao_2["id"],
            "resultado": "NEGATIVA",
        },
    ).json()["data"]
    authenticated_client.post(f"/api/microbiologia/culturas/{cultura_2['id']}/liberar")

    response = authenticated_client.get("/api/microbiologia/culturas/parciais")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["total"] == 1
    assert body["items"][0]["pendencia"] == "Aguardando resultado da cultura"


def test_marcar_isolado_sem_antibiograma_padronizado(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    ).json()["data"]
    isolado_id = criada["microrganismos"][0]["id"]
    assert criada["microrganismos"][0]["sem_antibiograma_padronizado"] is False

    response = authenticated_client.put(
        f"/api/microbiologia/isolados/{isolado_id}/sem-antibiograma",
        json={"sem_antibiograma_padronizado": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["sem_antibiograma_padronizado"] is True

    cultura_atualizada = authenticated_client.get(
        f"/api/microbiologia/culturas/{criada['id']}"
    ).json()["data"]
    assert cultura_atualizada["microrganismos"][0]["sem_antibiograma_padronizado"] is True


def test_marcar_isolado_sem_antibiograma_isolado_inexistente(authenticated_client):
    response = authenticated_client.put(
        "/api/microbiologia/isolados/00000000-0000-0000-0000-000000000000/sem-antibiograma",
        json={"sem_antibiograma_padronizado": True},
    )

    assert response.status_code == 404


def test_permite_liberar_cultura_positiva_com_isolado_dispensado_de_antibiograma(
    authenticated_client,
):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    ).json()["data"]
    isolado_id = criada["microrganismos"][0]["id"]

    authenticated_client.put(
        f"/api/microbiologia/isolados/{isolado_id}/sem-antibiograma",
        json={"sem_antibiograma_padronizado": True},
    )

    parciais = authenticated_client.get("/api/microbiologia/culturas/parciais").json()["data"]
    pendencia = next(item["pendencia"] for item in parciais["items"] if item["id"] == criada["id"])
    assert pendencia == "Pronta para liberação"

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 200
    assert response.json()["data"]["liberado_tecnicamente"] is True


def test_nao_permite_liberar_cultura_com_isolado_nao_dispensado_ainda_pendente(
    authenticated_client,
):
    """
    Cultura com 2 isolados: um dispensado (sem antibiograma padronizado) e
    outro sem essa marcação e sem antibiograma - a liberação deve
    continuar bloqueada por causa do isolado não dispensado.
    """
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo_1 = _criar_microrganismo(authenticated_client, nome="Klebsiella pneumoniae")
    microrganismo_2 = _criar_microrganismo(authenticated_client, nome="Escherichia coli")
    criada = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo_1["id"], microrganismo_2["id"]],
        },
    ).json()["data"]
    isolado_dispensado_id = criada["microrganismos"][0]["id"]

    authenticated_client.put(
        f"/api/microbiologia/isolados/{isolado_dispensado_id}/sem-antibiograma",
        json={"sem_antibiograma_padronizado": True},
    )

    response = authenticated_client.post(f"/api/microbiologia/culturas/{criada['id']}/liberar")

    assert response.status_code == 422
    assert "antibiograma" in response.json()["message"].lower()


def test_resultados_parciais_mostra_pendencia_de_antibiograma(authenticated_client):
    paciente = _criar_paciente(authenticated_client)
    solicitacao = _criar_solicitacao(authenticated_client, paciente["id"])
    microrganismo = _criar_microrganismo(authenticated_client)
    authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    )

    response = authenticated_client.get("/api/microbiologia/culturas/parciais")

    body = response.json()["data"]
    assert body["total"] == 1
    assert body["items"][0]["pendencia"] == "Aguardando antibiograma"
