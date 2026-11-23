from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select

from app.api.deps import DB, usuario_atual
from app.models import Correspondencia, PalavraChave
from app.schemas import PalavraChaveIn, PalavraChaveOut, PalavraChaveUpdate

router = APIRouter(
    prefix="/palavras-chave", tags=["palavras-chave"], dependencies=[Depends(usuario_atual)]
)


@router.get("", response_model=list[PalavraChaveOut])
def listar(db: DB):
    return db.scalars(select(PalavraChave).order_by(PalavraChave.id)).all()


@router.post("", response_model=PalavraChaveOut, status_code=201)
def criar(dados: PalavraChaveIn, db: DB):
    termo = dados.termo.strip()
    if db.scalar(select(PalavraChave).where(PalavraChave.termo == termo)):
        raise HTTPException(409, "Essa palavra-chave já existe")
    palavra = PalavraChave(termo=termo)
    db.add(palavra)
    db.commit()
    return palavra


@router.patch("/{palavra_id}", response_model=PalavraChaveOut)
def atualizar(palavra_id: int, dados: PalavraChaveUpdate, db: DB):
    palavra = db.get(PalavraChave, palavra_id)
    if palavra is None:
        raise HTTPException(404, "Palavra-chave não encontrada")
    palavra.ativa = dados.ativa
    db.commit()
    return palavra


@router.delete("/{palavra_id}", status_code=204)
def remover(palavra_id: int, db: DB):
    palavra = db.get(PalavraChave, palavra_id)
    if palavra is None:
        raise HTTPException(404, "Palavra-chave não encontrada")
    # remove antes as correspondências, que dependem da palavra (chave estrangeira)
    db.execute(delete(Correspondencia).where(Correspondencia.palavra_chave_id == palavra_id))
    db.delete(palavra)
    db.commit()
