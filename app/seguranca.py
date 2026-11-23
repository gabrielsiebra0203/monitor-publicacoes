from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app import config

ALGORITMO = "HS256"
_hasher = PasswordHash.recommended()
# usado quando o e-mail não existe, para o tempo de resposta não revelar isso
HASH_FALSO = _hasher.hash("senha-falsa-para-igualar-o-tempo")


def hash_senha(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, hash_: str) -> bool:
    return _hasher.verify(senha, hash_)


def _segredo() -> str:
    if len(config.JWT_SECRET) < 32:
        raise RuntimeError("Defina JWT_SECRET (mínimo 32 caracteres) no .env")
    return config.JWT_SECRET


def criar_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRA_MINUTOS)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, _segredo(), algorithm=ALGORITMO)


def decodificar_token(token: str) -> str:
    """Devolve o id do usuário (texto) ou levanta jwt.InvalidTokenError."""
    dados = jwt.decode(
        token, _segredo(), algorithms=[ALGORITMO], options={"require": ["exp", "sub"]}
    )
    return dados["sub"]
