# Client Manager

Sistema interno de uma empresa de investimentos que gerencia clientes e seu patrimônio investido, integrando-se ao Pipefy via GraphQL. As chamadas são enviadas de forma real para a API do Pipefy (`https://api.pipefy.com/graphql`) usando autenticação por Bearer token.

## Stack

- **Python 3.14**
- **FastAPI** — framework web, OpenAPI/Swagger automático
- **Pydantic v2** — validação de requisição e resposta
- **SQLAlchemy 2.0** — ORM
- **SQLite** — banco de dados local (arquivo `client_manager.db`)
- **requests** — cliente HTTP para chamadas à API GraphQL do Pipefy
- **pytest** — testes

## Executando localmente

```bash
# 1. Criar o ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
Windows
.\venv\Scripts\Activate.ps1

Mac / Linux
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite .env e preencha PIPEFY_TOKEN com seu token de acesso pessoal do Pipefy

# 5. Subir a API
uvicorn app.main:app --reload --port=8000
```

A API roda em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

> **Variáveis de ambiente obrigatória para integração com Pipefy**
>
> `PIPEFY_TOKEN`: Token de acesso pessoal do Pipefy (Personal Access Token). Obtido em **Pipefy → Perfil → Personal access tokens**. https://app.pipefy.com/tokens

## Executando os testes

```powershell
pytest -v
```

A suíte de testes usa SQLite in-memory; nenhum setup necessário.

## Exemplos de requisição

> **Nota:** Os exemplos abaixo usam `curl` no estilo Linux/macOS. No Windows, use Git Bash ou WSL (caracteres acentuados podem não funcionar no Git Bash), ou adapte para `Invoke-WebRequest` no PowerShell.

### Criar um cliente (`POST /clients`)

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

Resposta (`201 Created`):

```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao.silva@example.com",
  "request_type": "Atualização cadastral",
  "patrimony": 250000.0,
  "status": "Aguardando Análise",
  "priority": null,
  "card_id": "303886059"
}
```

A aplicação envia a mutation GraphQL `createCard` ao Pipefy e persiste o `id` retornado no campo `card_id`.

### Simular um webhook do Pipefy (`POST /webhooks/pipefy/card-updated`)

```bash
curl -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

Comportamento:

- Calcula a prioridade com base no patrimônio do cliente: `>= 200000` → `Alta`, caso contrário `Normal`.
- Atualiza o `status` do cliente para `Processado` e persiste a prioridade calculada.
- Envia a mutation GraphQL `updateFieldsValues` (status + prioridade) ao Pipefy.
- Registra o `event_id` para que o mesmo webhook seja ignorado em reenvios.

Respostas possíveis:

- `200 OK` — `{"status": "processed", "reason": null}`
- `200 OK` — `{"status": "ignored", "reason": "duplicated event"}` (idempotência)
- `404 Not Found` — cliente com aquele e-mail não existe
- `422 Unprocessable Entity` — payload inválido

## Arquitetura

Desenho em camadas com fluxo de dependência unidirecional:

```
API (FastAPI routers)
    │
    ▼
Service (regras de negócio)
    │
    ├──▶ Repository (SQLAlchemy)
    │
    └──▶ Integration (PipefyBase ABC)
                │
                └─ PipefyClient (integração com o funil de clientes do Pipefy via POST GraphQL)
```

## Estrutura do projeto

```
app/
├── api/v1/endpoints/    # Routers do FastAPI
├── core/                # config, database, exceptions
├── integrations/pipefy/ # Integração com Pipefy + mutations GraphQL
├── models/              # Models SQLAlchemy
├── repositories/        # Camada de acesso a dados
├── schemas/             # Schemas Pydantic + enums
├── services/            # Camada de regras de negócio
└── main.py              # Factory do FastAPI + lifespan
tests/                   # Espelha a estrutura de app/
```
