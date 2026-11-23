import argparse
import getpass
import logging
from datetime import date, timedelta

from sqlalchemy import select

from app import config, seguranca
from app.db import get_session
from app.fontes.querido_diario import QueridoDiario
from app.models import PalavraChave, Usuario
from app.servico import coletar, enviar_alertas
from app.telegram import enviar_mensagem

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
# o httpx registra a URL de cada requisição, e a do Telegram contém o token do bot
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def main() -> None:
    parser = argparse.ArgumentParser(prog="monitor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="adiciona uma palavra-chave")
    p_add.add_argument("termo")

    sub.add_parser("listar", help="lista as palavras-chave")

    p_user = sub.add_parser("criar-usuario", help="cria um usuário da API")
    p_user.add_argument("email")

    p_run = sub.add_parser("run", help="coleta e envia alertas")
    p_run.add_argument("--dias", type=int, default=config.DIAS_RETROATIVOS)
    p_run.add_argument("--limite", type=int, default=10)
    p_run.add_argument("--sem-telegram", action="store_true", help="só imprime no terminal")

    args = parser.parse_args()

    with get_session() as session:
        if args.cmd == "add":
            termo = args.termo.strip()
            if session.scalar(select(PalavraChave).where(PalavraChave.termo == termo)):
                print("Essa palavra-chave já existe.")
            else:
                session.add(PalavraChave(termo=termo))
                session.commit()
                print(f"Adicionada: {termo}")

        elif args.cmd == "listar":
            for p in session.scalars(select(PalavraChave).order_by(PalavraChave.id)):
                print(f"{p.id:>3}  {'ativa' if p.ativa else 'inativa':<8} {p.termo}")

        elif args.cmd == "criar-usuario":
            email = args.email.strip().lower()
            if session.scalar(select(Usuario).where(Usuario.email == email)):
                print("Esse usuário já existe.")
                return
            senha = getpass.getpass("Senha (mínimo 10 caracteres): ")
            if len(senha) < 10 or senha != getpass.getpass("Repita a senha: "):
                print("Senha curta demais ou diferente da repetição.")
                return
            session.add(Usuario(email=email, senha_hash=seguranca.hash_senha(senha)))
            session.commit()
            print(f"Usuário criado: {email}")

        elif args.cmd == "run":
            hoje = date.today()
            novas = coletar(session, QueridoDiario(), hoje - timedelta(days=args.dias), hoje)
            print(f"Correspondências novas: {novas}")
            enviar = print if args.sem_telegram else enviar_mensagem
            enviados = enviar_alertas(
                session, enviar, limite=args.limite, marcar=not args.sem_telegram
            )
            print(f"Alertas processados: {enviados}")


if __name__ == "__main__":
    main()
