# Client Manager

Esqueleto de um sistema interno de uma empresa de investimentos que gerencia clientes e seu patrimônio investido, mapeando ações para o Pipefy via GraphQL. As chamadas ao Pipefy não são enviadas pela rede — os payloads GraphQL são estruturados fielmente conforme a documentação oficial do Pipefy e logados por um client fake, pronto para ser substituído por uma implementação HTTP real.

## Stack

- **Python 3.14**
- **FastAPI** — framework web, OpenAPI/Swagger automático
- **Pydantic v2** — validação de requisição e resposta
- **SQLAlchemy 2.0** — ORM
- **SQLite** — banco de dados local (arquivo `client_manager.db`)
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

# 4. Subir a API
uvicorn app.main:app --reload
```

A API roda em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

## Executando os testes

```powershell
pytest -v
```

A suíte de testes usa SQLite in-memory; nenhum setup necessário.

## Exemplos de requisição

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
  "card_id": "card_fake_ab12cd34"
}
```

A aplicação loga o payload GraphQL `createCard` que seria enviado ao Pipefy.

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

- Calcula a prioridade com base no patrimônio do cliente: `>= 200000` → `prioridade_alta`, caso contrário `prioridade_normal`.
- Loga o payload GraphQL `updateFieldsValues` (status + prioridade) que seria enviado ao Pipefy.
- Atualiza o `status` do cliente para `Processado` e persiste a prioridade calculada.
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
    └──▶ Integration (PipefyClient ABC)
                │
                └─ FakePipefyClient (implementação atual, loga os payloads)
```

Decisões-chave:

- **Classe `Base` única** em `app/models/base.py` carrega as colunas compartilhadas (`id`, `created_at`, `updated_at`); models concretos herdam e adicionam seus próprios campos.
- **`BaseRepository[Model]` genérico** centraliza o CRUD; repositórios específicos adicionam apenas suas consultas.
- **O client do Pipefy é uma ABC**, injetada via `Depends`. Trocar o fake por uma implementação HTTP real não exige mudanças na camada de serviço (Dependency Inversion).
- **Schemas separados dos models**: Pydantic na borda da API, SQLAlchemy na borda da persistência. O `Field(alias=...)` permite que a API aceite as chaves em português exigidas pelo enunciado enquanto o código usa nomes de atributos em inglês.

## Estrutura do projeto

```
app/
├── api/v1/endpoints/    # Routers do FastAPI
├── core/                # config, database, exceptions
├── integrations/pipefy/ # PipefyClient ABC + FakePipefyClient + mutations GraphQL
├── models/              # Models SQLAlchemy
├── repositories/        # Camada de acesso a dados
├── schemas/             # Schemas Pydantic + enums
├── services/            # Regras de negócio
└── main.py              # Factory do FastAPI + lifespan
tests/                   # Espelha a estrutura de app/
```
