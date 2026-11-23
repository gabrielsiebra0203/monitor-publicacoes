from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import DB, usuario_atual
from app.models import Correspondencia, Publicacao
from app.schemas import CorrespondenciaOut, PublicacaoOut

router = APIRouter(tags=["consultas"], dependencies=[Depends(usuario_atual)])


@router.get("/publicacoes", response_model=list[PublicacaoOut])
def listar_publicacoes(
    db: DB,
    municipio: str | None = None,
    desde: date | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = select(Publicacao).order_by(Publicacao.data_publicacao.desc(), Publicacao.id.desc())
    if municipio:
        q = q.where(Publicacao.municipio.ilike(f"%{municipio}%"))
    if desde:
        q = q.where(Publicacao.data_publicacao >= desde)
    return db.scalars(q.limit(limit).offset(offset)).all()


@router.get("/correspondencias", response_model=list[CorrespondenciaOut])
def listar_correspondencias(
    db: DB,
    alertada: bool | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = (
        select(Correspondencia)
        .options(joinedload(Correspondencia.publicacao), joinedload(Correspondencia.palavra_chave))
        .order_by(Correspondencia.id.desc())
    )
    if alertada is not None:
        q = q.where(Correspondencia.alertada.is_(alertada))
    return db.scalars(q.limit(limit).offset(offset)).all()
