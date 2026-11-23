# Monitor de Publicações

Serviço que acompanha diários oficiais municipais, encontra publicações
com as palavras-chave que você escolher e envia alertas no Telegram.

## Como funciona
Coleta (agendada) → normalização e deduplicação → PostgreSQL →
correspondência por palavra-chave → alerta no Telegram.

## Stack
Python 3.14 · SQLAlchemy · PostgreSQL · Docker Compose · httpx · pytest · Telegram Bot API

## Decisões técnicas
- **Adaptador por fonte:** cada fonte de dados implementa a mesma interface,
  então adicionar uma nova não mexe no resto do sistema.
- **Tolerância a falhas:** a API externa é instável; o coletor tenta de novo
  com espera crescente e, se uma busca falhar, segue com as demais.
- **Sem alertas duplicados:** o envio é marcado a cada mensagem, então uma
  queda no meio da execução não repete avisos.
- **Limite por execução:** evita enxurradas e respeita os limites do Telegram.

## Como rodar
1. `cp .env.example .env` e preencha os valores
2. `docker compose up -d`
3. `python -m app.main init-db`
4. `python -m app.main add "licitação"`
5. `python -m app.main run --dias 7`

## Testes
`python -m pytest -v`

## Fonte dos dados
[Querido Diário](https://queridodiario.org.br), da Open Knowledge Brasil.

## Roadmap
- [ ] API REST com FastAPI e autenticação
- [ ] Migrações com Alembic
- [ ] CI/CD com GitHub Actions e deploy na VPS
- [ ] Segunda fonte: Diário Oficial do Estado do Ceará