import argparse
from datetime import date, timedelta

from sqlalchemy import select

from app import config
from app.db import get_engine, get_session
from app.fontes.querido_diario import QueridoDiario
from app.models import Base, PalavraChave
from app.servico import coletar, enviar_alertas
from app.telegram import enviar_mensagem


def main() -> None:
    parser = argparse.ArgumentParser(prog="monitor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db", help="cria as tabelas")

    p_add = sub.add_parser("add", help="adiciona uma palavra-chave")
    p_add.add_argument("termo")

    sub.add_parser("listar", help="lista as palavras-chave")

    p_run = sub.add_parser("run", help="coleta e envia alertas")
    p_run.add_argument("--dias", type=int, default=config.DIAS_RETROATIVOS)
    p_run.add_argument("--sem-telegram", action="store_true", help="só imprime no terminal")
    p_run.add_argument("--limite", type=int, default=10)

    args = parser.parse_args()

    if args.cmd == "init-db":
        Base.metadata.create_all(get_engine())
        print("Tabelas criadas.")
        return

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

        elif args.cmd == "run":
            hoje = date.today()
            novas = coletar(session, QueridoDiario(), hoje - timedelta(days=args.dias), hoje)
            print(f"Correspondências novas: {novas}")
            enviar = print if args.sem_telegram else enviar_mensagem
            print(f"Alertas processados: {enviar_alertas(session, enviar, limite=args.limite, marcar=not args.sem_telegram)}")


if __name__ == "__main__":
    main()