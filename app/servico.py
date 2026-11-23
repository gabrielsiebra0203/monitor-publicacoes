from datetime import date
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Correspondencia, PalavraChave, Publicacao
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
import httpx
import time
log = logging.getLogger(__name__)



def coletar(session: Session, fonte, desde: date, ate: date) -> int:
    """Busca palavras-chave ativas e grava novas correspondências."""
    novas = 0
    falhas = 0

    palavras = session.scalars(
        select(PalavraChave).where(PalavraChave.ativa.is_(True))
    ).all()

    for palavra in palavras:
        try:
            itens = fonte.buscar(palavra.termo, desde, ate)

        except httpx.HTTPStatusError as exc:
            falhas += 1
            log.warning(
                "Falha HTTP ao buscar '%s' em %s: status=%s",
                palavra.termo,
                fonte.nome,
                exc.response.status_code,
            )
            continue

        except httpx.RequestError as exc:
            falhas += 1
            log.warning(
                "Falha de conexão ao buscar '%s' em %s: %s",
                palavra.termo,
                fonte.nome,
                type(exc).__name__,
            )
            continue

        for item in itens:
            pub = session.scalar(
                select(Publicacao).where(Publicacao.url == item.url)
            )

            if pub is None:
                pub = Publicacao(
                    fonte=item.fonte,
                    municipio=item.municipio,
                    data_publicacao=item.data_publicacao,
                    edicao=item.edicao,
                    url=item.url,
                )
                session.add(pub)
                session.flush()

            ja_existe = session.scalar(
                select(Correspondencia).where(
                    Correspondencia.publicacao_id == pub.id,
                    Correspondencia.palavra_chave_id == palavra.id,
                )
            )

            if ja_existe is None:
                session.add(
                    Correspondencia(
                        publicacao_id=pub.id,
                        palavra_chave_id=palavra.id,
                        trecho="\n…\n".join(item.trechos),
                    )
                )
                novas += 1

        session.commit()

    if palavras and falhas == len(palavras):
        raise RuntimeError(
            "Coleta indisponível: todas as consultas à fonte falharam."
        )

    if falhas:
        log.warning(
            "Coleta parcialmente concluída: %s de %s consultas falharam.",
            falhas,
            len(palavras),
        )

    return novas



def formatar_alerta(c: Correspondencia) -> str:
    p = c.publicacao
    return (
        f"🔔 Palavra-chave: {c.palavra_chave.termo}\n"
        f"📍 {p.municipio} — {p.data_publicacao:%d/%m/%Y}\n\n"
        f"{c.trecho}\n\n"
        f"🔗 {p.url}"
    )


def enviar_alertas(
    session: Session,
    enviar: Callable[[str], None],
    limite: int = 10,
    pausa: float = 1.0,
    marcar: bool = True,
) -> int:
    """Envia até `limite` alertas pendentes. O resto fica para a próxima execução."""
    pendentes = session.scalars(
        select(Correspondencia)
        .where(Correspondencia.alertada.is_(False))
        .order_by(Correspondencia.id)
    ).all()

    lote, restante = pendentes[:limite], max(0, len(pendentes) - limite)
    for c in lote:
        enviar(formatar_alerta(c))
        if marcar:
            c.alertada = True
            session.commit()  # commit a cada envio: se cair no meio, não repete
        time.sleep(pausa)

    if restante:
        enviar(f"ℹ️ Mais {restante} alertas pendentes serão enviados nas próximas execuções.")
    return len(lote)