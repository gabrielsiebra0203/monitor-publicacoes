from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PalavraChaveIn(BaseModel):
    termo: str = Field(min_length=2, max_length=200)


class PalavraChaveUpdate(BaseModel):
    ativa: bool


class PalavraChaveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    termo: str
    ativa: bool


class PublicacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fonte: str
    municipio: str
    data_publicacao: date
    edicao: str | None
    url: str


class CorrespondenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    trecho: str
    alertada: bool
    publicacao: PublicacaoOut
    palavra_chave: PalavraChaveOut


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
