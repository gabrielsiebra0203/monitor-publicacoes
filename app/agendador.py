
import logging
import signal
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler

from app import config
from app.db import get_session
from app.fontes.querido_diario import QueridoDiario
from app.servico import coletar, enviar_alertas
from app.telegram import enviar_mensagem


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

log = logging.getLogger(__name__)

# Evita que logs HTTP exponham URLs com o token do Telegram.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

FUSO = ZoneInfo("America/Fortaleza")



def executar_monitoramento() -> None:
    """Executa a coleta e processa alertas pendentes."""

    agora = datetime.now(FUSO)
    hoje = agora.date()
    desde = hoje - timedelta(days=config.DIAS_RETROATIVOS)

    log.info("Iniciando monitoramento: %s até %s", desde, hoje)

    with get_session() as session:
        fonte = QueridoDiario()

        try:
            novas = coletar(
                session=session,
                fonte=fonte,
                desde=desde,
                ate=hoje,
            )
            log.info("Novas correspondências: %s", novas)

        except RuntimeError as exc:
            session.rollback()
            log.warning("Coleta não concluída: %s", exc)

        finally:
            fonte.client.close()

        # O envio acontece independentemente do resultado da coleta.
        try:
            enviados = enviar_alertas(
                session=session,
                enviar=enviar_mensagem,
                limite=10,
            )
            log.info("Alertas enviados: %s", enviados)

        except Exception:
            session.rollback()
            log.exception("Falha durante o envio dos alertas")
            raise





def main():
    scheduler = BlockingScheduler(timezone=FUSO)

    scheduler.add_job(
        executar_monitoramento,
        trigger="cron",
        hour="8,18",
        minute=0,
        id="monitorar_publicacoes",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
        replace_existing=True,
    )

    def solicitar_encerramento(signum, frame):
        log.info(
            "Sinal %s recebido. Solicitando encerramento do agendador...",
            signum,
        )

        if scheduler.running:
            scheduler.shutdown(wait=False)

    signal.signal(signal.SIGTERM, solicitar_encerramento)
    signal.signal(signal.SIGINT, solicitar_encerramento)

    log.info("Agendador iniciado: execuções às 08h e 18h")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Agendador interrompido.")

    log.info("Processo do agendador finalizado.")
if __name__ == "__main__":
    main()


