
from datetime import date
from unittest.mock import MagicMock, patch

from app import agendador


def test_executar_monitoramento():
    session = MagicMock()
    contexto = MagicMock()
    contexto.__enter__.return_value = session

    fonte = MagicMock()

    with (
        patch.object(agendador, "get_session", return_value=contexto),
        patch.object(agendador, "QueridoDiario", return_value=fonte),
        patch.object(agendador, "coletar", return_value=2) as coleta,
        patch.object(
            agendador, "enviar_alertas", return_value=2
        ) as alertas,
    ):
        agendador.executar_monitoramento()

    coleta.assert_called_once()
    alertas.assert_called_once()

    argumentos = coleta.call_args.kwargs

    assert argumentos["session"] is session
    assert argumentos["fonte"] is fonte
    assert isinstance(argumentos["desde"], date)
    assert isinstance(argumentos["ate"], date)

    fonte.client.close.assert_called_once()

def test_envia_alertas_mesmo_com_falha_na_coleta():
    session = MagicMock()
    contexto = MagicMock()
    contexto.__enter__.return_value = session

    fonte = MagicMock()

    with (
        patch.object(agendador, "get_session", return_value=contexto),
        patch.object(agendador, "QueridoDiario", return_value=fonte),
        patch.object(
            agendador,
            "coletar",
            side_effect=RuntimeError("API indisponível"),
        ) as coleta,
        patch.object(
            agendador,
            "enviar_alertas",
            return_value=3,
        ) as alertas,
    ):
        agendador.executar_monitoramento()

    coleta.assert_called_once()
    session.rollback.assert_called_once()
    alertas.assert_called_once()
    fonte.client.close.assert_called_once()
