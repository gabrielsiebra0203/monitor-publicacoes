from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.fontes.base import PublicacaoEncontrada
from app.models import Base, PalavraChave
from app.servico import coletar, enviar_alertas


class FonteFalsa:
    nome = "falsa"

    def buscar(self, termo, desde, ate):
        return [
            PublicacaoEncontrada(
                fonte="falsa",
                municipio="Fortaleza",
                data_publicacao=date(2026, 11, 20),
                edicao="1",
                url="https://exemplo.org/a.pdf",
                trechos=[f"trecho sobre {termo}"],
            )
        ]


def nova_sessao() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add(PalavraChave(termo="licitação"))
    session.commit()
    return session


def test_coletar_nao_duplica():
    s = nova_sessao()
    desde, ate = date(2026, 11, 15), date(2026, 11, 22)
    assert coletar(s, FonteFalsa(), desde, ate) == 1
    assert coletar(s, FonteFalsa(), desde, ate) == 0


def test_alerta_e_enviado_uma_unica_vez():
    s = nova_sessao()
    coletar(s, FonteFalsa(), date(2026, 11, 15), date(2026, 11, 22))
    mensagens: list[str] = []

    assert enviar_alertas(s, mensagens.append) == 1
    assert enviar_alertas(s, mensagens.append) == 0
    assert "licitação" in mensagens[0]