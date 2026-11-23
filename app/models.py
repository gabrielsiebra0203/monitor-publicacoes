from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def agora() -> datetime:
    return datetime.now(timezone.utc)


class PalavraChave(Base):
    __tablename__ = "palavras_chave"

    id: Mapped[int] = mapped_column(primary_key=True)
    termo: Mapped[str] = mapped_column(String(200), unique=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Publicacao(Base):
    __tablename__ = "publicacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    fonte: Mapped[str] = mapped_column(String(50))
    municipio: Mapped[str] = mapped_column(String(120))
    data_publicacao: Mapped[date] = mapped_column(Date)
    edicao: Mapped[str | None] = mapped_column(String(50), nullable=True)
    url: Mapped[str] = mapped_column(String(500), unique=True)
    coletada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Correspondencia(Base):
    __tablename__ = "correspondencias"
    __table_args__ = (UniqueConstraint("publicacao_id", "palavra_chave_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    publicacao_id: Mapped[int] = mapped_column(ForeignKey("publicacoes.id"))
    palavra_chave_id: Mapped[int] = mapped_column(ForeignKey("palavras_chave.id"))
    trecho: Mapped[str] = mapped_column(Text, default="")
    alertada: Mapped[bool] = mapped_column(Boolean, default=False)

    publicacao: Mapped[Publicacao] = relationship()
    palavra_chave: Mapped[PalavraChave] = relationship()