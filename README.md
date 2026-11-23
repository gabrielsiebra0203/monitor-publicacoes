# 🔔 Monitor de Publicações

Sistema de monitoramento automatizado de publicações em diários oficiais municipais, desenvolvido em Python, com API REST, autenticação JWT, PostgreSQL e notificações pelo Telegram.

O projeto utiliza a API do Querido Diário para localizar publicações relacionadas a palavras-chave cadastradas.

## 🎯 Objetivo

Automatizar a busca por informações em diários oficiais, reduzindo a necessidade de consultas manuais e permitindo o acompanhamento de termos de interesse.

## 🚀 Funcionalidades

- Cadastro e gerenciamento de palavras-chave
- Consulta à API do Querido Diário
- Monitoramento de municípios configuráveis
- Armazenamento de publicações no PostgreSQL
- Deduplicação de publicações e correspondências
- Envio de notificações pelo Telegram
- API REST desenvolvida com FastAPI
- Autenticação JWT
- Migrações de banco com Alembic
- Agendamento automático com APScheduler
- Tratamento de falhas e tentativas automáticas
- Implantação com Docker Compose em VPS Linux

## 🛠️ Tecnologias

| Tecnologia | Utilização |
|------------|------------|
| Python 3.14 | Desenvolvimento da aplicação |
| FastAPI | API REST |
| PostgreSQL 16 | Banco de dados |
| SQLAlchemy | ORM |
| Alembic | Migrações |
| APScheduler | Agendamento |
| Docker Compose | Orquestração de contêineres |
| httpx | Integração HTTP |
| JWT | Autenticação |
| Telegram Bot API | Notificações |
| pytest | Testes automatizados |
| Linux | Ambiente de implantação |

## 🏗️ Arquitetura

```text
              APScheduler
                   |
                   v
          Coletor Python
                   |
                   v
          API Querido Diário
                   |
                   v
       Processamento dos dados
                   |
                   v
             PostgreSQL
                   |
                   v
          Correspondências
                   |
                   v
             Telegram

FastAPI + JWT
     |
     v
Gerenciamento de palavras-chave
e consulta às correspondências
     |
     v
PostgreSQL
```

## ⚙️ Configuração

### 1. Clonar o repositório

```bash
git clone https://github.com/gabrielsiebra0203/monitor-publicacoes.git
cd monitor-publicacoes
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Preencha as configurações de PostgreSQL, Telegram, municípios monitorados e autenticação JWT.

Nunca publique o arquivo `.env` com credenciais reais.

### 3. Iniciar o banco de dados

```bash
docker compose up -d db
```

### 4. Executar as migrações

```bash
docker compose run --rm api alembic upgrade head
```

### 5. Iniciar a API

```bash
docker compose up -d api
```

A documentação interativa estará disponível em:

```text
http://localhost:8000/docs
```

### 6. Criar um usuário

```bash
docker compose exec api python -m app.main criar-usuario usuario@exemplo.com
```

O comando solicitará uma senha.

### 7. Cadastrar uma palavra-chave

```bash
docker compose exec api python -m app.main add "licitação"
```

### 8. Executar uma coleta manual

```bash
docker compose exec api python -m app.main run --dias 7 --sem-telegram
```

Esse modo permite visualizar alertas sem enviá-los ao Telegram.

### 9. Iniciar o agendador

```bash
docker compose --profile monitoramento up -d agendador
```

O monitoramento está configurado para executar diariamente às:

- 08h — horário de Fortaleza
- 18h — horário de Fortaleza

## 🔐 Segurança

- Autenticação com JWT
- Senhas armazenadas com hash
- Credenciais em variáveis de ambiente
- Endpoints protegidos
- Banco PostgreSQL acessível pela rede interna do Docker
- Tratamento de erros sem exposição do token do Telegram nos logs HTTP

## 🧪 Testes

```bash
python -m pytest -v
```

## 🖥️ Implantação

O projeto foi implantado em uma VPS Linux utilizando Docker Compose, com três serviços:

- PostgreSQL
- FastAPI
- APScheduler

A API, a autenticação JWT, o banco de dados e o envio de mensagens pelo Telegram foram validados no ambiente de implantação.

O agendador também foi iniciado e configurado para execução automática.

**Observação:** a coleta completa em produção ainda depende da disponibilidade da API externa do Querido Diário, que apresentou respostas HTTP 503 durante os testes.

## 📌 Decisões técnicas

**Adaptador por fonte:** permite adicionar novas fontes de dados com menor acoplamento.

**Tolerância a falhas:** novas tentativas com espera progressiva em caso de indisponibilidade temporária.

**Deduplicação:** evita armazenar repetidamente a mesma correspondência.

**Controle de notificações:** mantém o estado dos alertas enviados e pendentes.

**Processamento em lotes:** limita a quantidade de notificações por execução.

## 🗺️ Roadmap

- [x] Coleta de publicações municipais
- [x] Persistência com PostgreSQL
- [x] API REST com FastAPI
- [x] Autenticação JWT
- [x] Migrações com Alembic
- [x] Notificações pelo Telegram
- [x] Agendamento automático
- [x] Implantação em VPS Linux
- [ ] Validar coleta completa em produção
- [ ] CI/CD com GitHub Actions
- [ ] Integração com outras fontes oficiais
- [ ] Dashboard web para acompanhamento

## 📚 Fonte dos dados

[Querido Diário — Open Knowledge Brasil](https://queridodiario.org.br)

## 👨‍💻 Autor

Gabriel Braga Siebra

[GitHub](https://github.com/gabrielsiebra0203)
