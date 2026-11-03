#  Auvren — Gestão Inteligente de Chamados

> **Plataforma web para gerenciamento de chamados de suporte, triagem assistida por inteligência artificial e acompanhamento de solicitações em organizações.**

## - Sobre o projeto

O **Auvren** é uma aplicação full stack desenvolvida para centralizar solicitações de suporte técnico e apoiar o atendimento com **triagem por IA**. O projeto combina uma API REST em Python, interface web em React e persistência em PostgreSQL, com foco em organização do código, testes automatizados e controle de acesso.

A plataforma permite registrar e acompanhar chamados, classificar solicitações por categoria e prioridade, atualizar status, consultar o histórico de alterações e visualizar indicadores de atendimento.

## - Funcionalidades

- **Chamados:** criação, listagem, consulta de detalhes e acompanhamento por status (*aberto*, *em andamento* e *resolvido*).
- **Organização:** categorias, prioridades, filtros, pesquisa, ordenação e paginação na API.
- **Triagem com IA:** integração com o **Google Gemini** para apoiar a análise dos chamados.
- **Dashboard:** indicadores de chamados totais, abertos, em andamento e resolvidos.
- **Histórico:** registro e consulta de alterações de status.
- **Gestão de usuários:** cadastro de integrantes da organização com perfis distintos.
- **Segurança:** autenticação JWT, autorização por papéis e isolamento dos dados por organização e usuário.

### - Perfis de acesso

| Perfil | Acesso |
| --- | --- |
| **Administrador (`admin`)** | Gerencia usuários e acessa os recursos de atendimento da organização. |
| **Agente (`agent`)** | Consulta, realiza triagem e atualiza chamados da organização. |
| **Funcionário (`requester`)** | Cria e acompanha somente os próprios chamados, sem permissão para alterar seu status. |

As permissões são aplicadas na **API**, além das restrições de navegação na interface.

## - Tecnologias utilizadas

| Camada | Tecnologias |
| --- | --- |
| **Backend** | Python 3.14, FastAPI, SQLAlchemy, Alembic, Pydantic |
| **Banco de dados** | PostgreSQL 16 (ambiente containerizado) |
| **Autenticação** | JWT, PyJWT, pwdlib/Argon2 |
| **Inteligência artificial** | Google Gemini (`google-genai`) |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS |
| **Estado e comunicação** | TanStack Query, Zustand, Axios, React Router |
| **Testes** | Pytest, pytest-cov, HTTPX |
| **Infraestrutura** | Dockerfile, Docker Compose |
| **Documentação da API** | OpenAPI / Swagger UI |

## - Estrutura do projeto

```text
Auvren/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── .env.example
└── README.md
```

## - Como executar localmente

O projeto oferece um ambiente **Docker Compose para o banco de dados e a API**. O frontend é iniciado separadamente com Vite.

### Pré-requisitos

- Git;
- Docker com suporte a Compose (ou ambiente compatível com Compose);
- Node.js e npm para o frontend;
- Chave de API do Google Gemini para usar os recursos de IA.

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>
```

> Substitua os campos acima pela URL e pelo nome reais do repositório.

### 2. Configurar as variáveis de ambiente

Na raiz do projeto:

```bash
cp .env.example .env
```

Edite `.env` e configure pelo menos:

```dotenv
JWT_SECRET_KEY=<SEGREDO_LONGO_E_ALEATORIO>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=<SUA_CHAVE_GEMINI>
GEMINI_MODEL=gemini-3.5-flash
POSTGRES_PASSWORD=<SENHA_FORTE_DO_POSTGRES>
```

**Importante:** no Docker Compose, a variável `DATABASE_URL` é montada automaticamente pelo serviço `api`, apontando para o container `db`. O valor local de exemplo presente no `.env.example` não é usado como conexão do serviço `api` nesse cenário.

Não envie o arquivo `.env` ao GitHub. Confirme também que o modelo Gemini configurado está disponível para sua chave.

### 3. Iniciar o PostgreSQL e a API

```bash
docker compose up --build -d
```

O Compose inicia o PostgreSQL, aguarda o banco ficar saudável e sobe a API. Na inicialização da API, o container executa `alembic upgrade head` antes do Uvicorn.

Para acompanhar a inicialização:

```bash
docker compose logs -f api
```

A API estará disponível em:

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### 4. Iniciar o frontend

Em outro terminal:

```bash
cd frontend
cp .env.example .env
npm ci
npm run dev
```

O arquivo `frontend/.env.example` já configura:

```dotenv
VITE_API_URL=http://localhost:8000
```

Acesse o endereço indicado pelo Vite no terminal (normalmente `http://localhost:5173`).

### 5. Encerrar os serviços

Na raiz do projeto:

```bash
docker compose down
```

O volume do PostgreSQL é preservado. **Atenção:** `docker compose down -v` também remove o volume e os dados persistidos.

## - Execução manual do backend (sem Docker)

Para executar a API diretamente, é necessário ter **Python 3.14** e um **PostgreSQL acessível**, com banco e usuário previamente configurados.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Configure o `.env` da raiz com uma conexão válida para seu PostgreSQL local, por exemplo:

```dotenv
DATABASE_URL=postgresql+psycopg://<USUARIO>:<SENHA>@localhost:5432/<BANCO>
```

Em seguida:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

> A instalação manual do PostgreSQL, a criação do banco e as credenciais dependem do ambiente de cada desenvolvedor. Não reutilize a senha ilustrativa do `.env.example`.

## - Testes e validação

O backend utiliza **Pytest**. No ambiente de desenvolvimento:

```bash
cd backend
source .venv/bin/activate
pytest
```

**Resultados registrados durante o desenvolvimento da v0.1.0:**

- **118 testes automatizados do backend aprovados**;
- **19 testes funcionais manuais do portal do funcionário aprovados**;
- **Nenhuma falha nos 19 cenários funcionais avaliados**.

Os cenários manuais incluíram autenticação, criação e consulta de chamados, histórico, permissões, isolamento entre funcionários e troca de sessões. Esses resultados não substituem uma auditoria de segurança ou testes de carga.

## - Estado do projeto

**v0.1.0 — MVP funcional, validado em ambiente local.**

A publicação de uma demonstração online e eventuais melhorias de produção são etapas posteriores.

## - Licença

A definir. Até a inclusão de um arquivo `LICENSE`, não se presume uma licença de uso ou redistribuição.