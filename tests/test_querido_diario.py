from datetime import date

import httpx
import respx

from app.fontes.querido_diario import QueridoDiario


@respx.mock
def test_buscar_converte_resposta_da_api():
    respx.get("https://api.queridodiario.org.br/gazettes").mock(
        return_value=httpx.Response(
            200,
            json={
                "total_gazettes": 1,
                "gazettes": [
                    {
                        "territory_id": "2304400",
                        "territory_name": "Fortaleza",
                        "date": "2026-11-20",
                        "edition": "123",
                        "url": "https://exemplo.org/diario.pdf",
                        "excerpts": ["  ...aviso de licitação...  "],
                    }
                ],
            },
        )
    )

    fonte = QueridoDiario(territory_ids=["2304400"], pausa=0)
    resultado = fonte.buscar("licitação", date(2026, 11, 15), date(2026, 11, 22))

    assert len(resultado) == 1
    assert resultado[0].municipio == "Fortaleza"
    assert resultado[0].data_publicacao == date(2026, 11, 20)
    assert resultado[0].trechos == ["...aviso de licitação..."]
@respx.mock
def test_buscar_tenta_de_novo_apos_503():
    rota = respx.get("https://api.queridodiario.org.br/gazettes").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json={"total_gazettes": 0, "gazettes": []}),
        ]
    )
    fonte = QueridoDiario(territory_ids=["2304400"], pausa=0, espera=0)

    assert fonte.buscar("licitação", date(2026, 11, 1), date(2026, 11, 2)) == []
    assert rota.call_count == 2