from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app import seguranca
from app.api.deps import DB
from app.models import Usuario
from app.schemas import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    usuario = db.scalar(select(Usuario).where(Usuario.email == form.username.strip().lower()))
    hash_ = usuario.senha_hash if usuario else seguranca.HASH_FALSO
    senha_ok = seguranca.verificar_senha(form.password, hash_)
    if usuario is None or not senha_ok:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=seguranca.criar_token(usuario.id))
