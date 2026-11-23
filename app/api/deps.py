from collections.abc import Iterator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import seguranca
from app.db import get_session
from app.models import Usuario

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Iterator[Session]:
    with get_session() as session:
        yield session


DB = Annotated[Session, Depends(get_db)]


def usuario_atual(token: Annotated[str, Depends(oauth2)], db: DB) -> Usuario:
    erro = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        usuario_id = int(seguranca.decodificar_token(token))
    except (jwt.InvalidTokenError, ValueError):
        raise erro from None
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise erro
    return usuario
