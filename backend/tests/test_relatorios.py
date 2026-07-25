"""
Testes do módulo Relatórios (Sprint 10).

Como os endpoints retornam arquivos binários (não o contrato JSON
padrão), os testes verificam: status HTTP, content-type, headers de
download e a assinatura binária do arquivo gerado (magic bytes).
"""


def test_exportar_pacientes_excel(authenticated_client):
    authenticated_client.post("/api/pacientes", json={"nome": "Paciente Relatório", "prontuario": "r1"})

    response = authenticated_client.get("/api/relatorios/pacientes.xlsx")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment" in response.headers["content-disposition"]
    # arquivos .xlsx são arquivos ZIP - começam com a assinatura "PK"
    assert response.content[:2] == b"PK"


def test_exportar_solicitacoes_excel(authenticated_client):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Relatório 2", "prontuario": "r2"}
    ).json()["data"]
    authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente["id"], "material": "Urina"}
    )

    response = authenticated_client.get("/api/relatorios/solicitacoes.xlsx")

    assert response.status_code == 200
    assert response.content[:2] == b"PK"


def test_exportar_culturas_parciais_excel(authenticated_client):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Parcial", "prontuario": "rp1"}
    ).json()["data"]
    solicitacao = authenticated_client.post(
        "/api/solicitacoes", json={"paciente_id": paciente["id"], "material": "Hemocultura"}
    ).json()["data"]
    authenticated_client.post("/api/microbiologia/culturas", json={"solicitacao_id": solicitacao["id"]})

    response = authenticated_client.get("/api/relatorios/culturas-parciais.xlsx")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content[:2] == b"PK"


def test_exportar_ccih_pdf(authenticated_client):
    paciente = authenticated_client.post(
        "/api/pacientes", json={"nome": "Paciente Relatório 3", "prontuario": "r3"}
    ).json()["data"]
    solicitacao = authenticated_client.post(
        "/api/solicitacoes",
        json={"paciente_id": paciente["id"], "material": "Hemocultura", "origem": "UTI"},
    ).json()["data"]
    microrganismo = authenticated_client.post(
        "/api/microrganismos", json={"nome": "Micro Relatório"}
    ).json()["data"]
    authenticated_client.post(
        "/api/microbiologia/culturas",
        json={
            "solicitacao_id": solicitacao["id"],
            "resultado": "POSITIVA",
            "microrganismo_ids": [microrganismo["id"]],
        },
    )

    response = authenticated_client.get("/api/relatorios/ccih.pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    # arquivos PDF começam com a assinatura "%PDF"
    assert response.content[:4] == b"%PDF"


def test_exportar_ccih_pdf_com_periodo_customizado(authenticated_client):
    response = authenticated_client.get(
        "/api/relatorios/ccih.pdf",
        params={"data_inicio": "2026-01-01", "data_fim": "2026-01-31"},
    )
    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"
