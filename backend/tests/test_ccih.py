"""
Testes do módulo CCIH (Sprint 9).
"""
from datetime import date, timedelta


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


def _fluxo_positivo_com_antibiograma(
    authenticated_client, prontuario, origem="UTI", nome_micro="Klebsiella pneumoniae", resultado_sir="RESISTENTE"
):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente CCIH", "prontuario": prontuario}
    ).json()["data"]
    solicitacao = authenticated_client.post(
        "/api/solicitacoes",
        json={"paciente_id": paciente["id"], "material": "Hemocultura", "origem": origem},
    ).json()["data"]
    microrganismo = _get_or_criar_microrganismo(authenticated_client, nome_micro)
    cultura = authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    ).json()["data"]
    isolado_id = cultura["microrganismos"][0]["id"]

    antimicrobiano = authenticated_client.post(
        "/api/antimicrobianos", json={"nome": f"Antimicrobiano {prontuario}"}
    ).json()["data"]
    authenticated_client.post(
        "/api/antibiogramas",
        json={
            "cultura_microrganismo_id": isolado_id,
            "resultados": [
                {"antimicrobiano_id": antimicrobiano["id"], "resultado": resultado_sir}
            ],
        },
    )

    return paciente, solicitacao, cultura


def test_indicadores_estrutura_basica(authenticated_client):
    response = authenticated_client.get("/api/ccih/indicadores")
    assert response.status_code == 200
    body = response.json()["data"]
    for campo in (
        "periodo_inicio",
        "periodo_fim",
        "total_solicitacoes",
        "total_culturas_positivas",
        "taxa_positividade",
        "distribuicao_por_setor",
        "perfil_microbiologico",
        "taxa_resistencia",
    ):
        assert campo in body


def test_total_solicitacoes_e_culturas_positivas(authenticated_client):
    _fluxo_positivo_com_antibiograma(authenticated_client, "c1")
    _fluxo_positivo_com_antibiograma(authenticated_client, "c2")

    body = authenticated_client.get("/api/ccih/indicadores").json()["data"]
    assert body["total_solicitacoes"] == 2
    assert body["total_culturas_positivas"] == 2
    assert body["taxa_positividade"] == 100.0


def test_distribuicao_por_setor(authenticated_client):
    _fluxo_positivo_com_antibiograma(authenticated_client, "c3", origem="UTI")
    _fluxo_positivo_com_antibiograma(authenticated_client, "c4", origem="Enfermaria")

    body = authenticated_client.get("/api/ccih/indicadores").json()["data"]
    setores = {item["setor"]: item["total_positivas"] for item in body["distribuicao_por_setor"]}
    assert setores.get("UTI") == 1
    assert setores.get("Enfermaria") == 1


def test_filtro_por_setor(authenticated_client):
    _fluxo_positivo_com_antibiograma(
        authenticated_client, "c10", origem="UTI", resultado_sir="RESISTENTE"
    )
    _fluxo_positivo_com_antibiograma(
        authenticated_client, "c11", origem="Enfermaria", resultado_sir="SENSIVEL"
    )

    body = authenticated_client.get(
        "/api/ccih/indicadores", params={"origem": "UTI"}
    ).json()["data"]

    assert body["filtro_setor"] == "UTI"
    assert body["total_solicitacoes"] == 1
    assert body["total_culturas_positivas"] == 1
    assert [item["setor"] for item in body["distribuicao_por_setor"]] == ["UTI"]
    assert len(body["taxa_resistencia"]) == 1
    assert body["taxa_resistencia"][0]["antimicrobiano"] == "Antimicrobiano c10"


def test_perfil_microbiologico_calcula_percentual(authenticated_client):
    _fluxo_positivo_com_antibiograma(authenticated_client, "c5", nome_micro="Klebsiella pneumoniae")
    _fluxo_positivo_com_antibiograma(authenticated_client, "c6", nome_micro="Klebsiella pneumoniae")
    _fluxo_positivo_com_antibiograma(authenticated_client, "c7", nome_micro="Escherichia coli")

    body = authenticated_client.get("/api/ccih/indicadores").json()["data"]
    perfil = {p["microrganismo"]: p for p in body["perfil_microbiologico"]}

    assert perfil["Klebsiella pneumoniae"]["quantidade"] == 2
    assert perfil["Klebsiella pneumoniae"]["percentual"] == 66.7
    assert perfil["Escherichia coli"]["quantidade"] == 1


def test_taxa_resistencia(authenticated_client):
    _fluxo_positivo_com_antibiograma(authenticated_client, "c8", resultado_sir="RESISTENTE")

    body = authenticated_client.get("/api/ccih/indicadores").json()["data"]
    assert len(body["taxa_resistencia"]) == 1
    item = body["taxa_resistencia"][0]
    assert item["total_testado"] == 1
    assert item["total_resistente"] == 1
    assert item["percentual_resistente"] == 100.0
    assert item["total_sensivel"] == 0
    assert item["percentual_sensivel"] == 0.0


def test_taxa_sensibilidade_mesmo_antimicrobiano(authenticated_client):
    # Duas culturas testadas contra o "mesmo" antimicrobiano (mesmo prontuário
    # usado como sufixo do nome em _fluxo_positivo_com_antibiograma) - uma
    # resistente, outra sensível - para conferir que os dois percentuais são
    # calculados sobre o total testado, não isoladamente.
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente CCIH Sensibilidade", "prontuario": "c9"}
    ).json()["data"]
    antimicrobiano = authenticated_client.post(
        "/api/antimicrobianos", json={"nome": "Antimicrobiano c9"}
    ).json()["data"]

    for resultado_sir in ("RESISTENTE", "SENSIVEL"):
        solicitacao = authenticated_client.post(
            "/api/solicitacoes",
            json={"paciente_id": paciente["id"], "material": "Hemocultura", "origem": "UTI"},
        ).json()["data"]
        microrganismo = _get_or_criar_microrganismo(authenticated_client, "Klebsiella pneumoniae")
        cultura = authenticated_client.post(
            "/api/microbiologia/culturas",
            json={
                "solicitacao_id": solicitacao["id"],
                "resultado": "POSITIVA",
                "microrganismo_ids": [microrganismo["id"]],
            },
        ).json()["data"]
        isolado_id = cultura["microrganismos"][0]["id"]
        authenticated_client.post(
            "/api/antibiogramas",
            json={
                "cultura_microrganismo_id": isolado_id,
                "resultados": [
                    {"antimicrobiano_id": antimicrobiano["id"], "resultado": resultado_sir}
                ],
            },
        )

    body = authenticated_client.get("/api/ccih/indicadores").json()["data"]
    item = next(
        r for r in body["taxa_resistencia"] if r["antimicrobiano"] == "Antimicrobiano c9"
    )
    assert item["total_testado"] == 2
    assert item["total_resistente"] == 1
    assert item["percentual_resistente"] == 50.0
    assert item["total_sensivel"] == 1
    assert item["percentual_sensivel"] == 50.0


def test_periodo_customizado_exclui_dados_fora_do_intervalo(authenticated_client):
    _fluxo_positivo_com_antibiograma(authenticated_client, "c9")

    ontem = date.today() - timedelta(days=1)
    anteontem = date.today() - timedelta(days=2)

    response = authenticated_client.get(
        "/api/ccih/indicadores",
        params={"data_inicio": anteontem.isoformat(), "data_fim": ontem.isoformat()},
    )

    body = response.json()["data"]
    assert body["total_culturas_positivas"] == 0
