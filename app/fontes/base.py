from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class PublicacaoEncontrada:
    fonte: str
    municipio: str
    data_publicacao: date
    edicao: str | None
    url: str
    trechos: list[str] = field(default_factory=list)


class Fonte(Protocol):
    nome: str

    def buscar(self, termo: str, desde: date, ate: date) -> list[PublicacaoEncontrada]:
        ...