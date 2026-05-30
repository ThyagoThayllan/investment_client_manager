import json
import logging
from uuid import uuid4

from app.integrations.pipefy.base import PipefyClient
from app.integrations.pipefy.mutations import CREATE_CARD_MUTATION
from app.integrations.pipefy.mutations import UPDATE_CARD_FIELDS_MUTATION
from app.models.client import Client
from app.schemas.client import ClientStatus
from app.schemas.client import Priority

logger = logging.getLogger(__name__)


class FakePipefyClient(PipefyClient):
    def _log_payload(self, mutation: str, variables: dict) -> None:
        payload = {'query': mutation.strip(), 'variables': variables}

        logger.info('Pipefy GraphQL payload: %s', json.dumps(payload, ensure_ascii=False))

    def create_card(self, client: Client) -> str:
        variables = {
            'input': {
                'pipe_id': 'FAKE_PIPE_ID',
                'fields_attributes': [
                    {'field_id': 'cliente_nome', 'field_value': client.name},
                    {'field_id': 'cliente_email', 'field_value': client.email},
                    {'field_id': 'valor_patrimonio', 'field_value': client.patrimony},
                ],
            },
        }

        self._log_payload(CREATE_CARD_MUTATION, variables)

        return f'card_fake_{uuid4().hex[:8]}'

    def mark_card_as_processed(self, card_id: str, priority: Priority) -> None:
        variables: dict[str, object] = {
            'input': {
                'nodeId': card_id,
                'values': [
                    {'fieldId': 'status', 'value': ClientStatus.PROCESSED.value},
                    {'fieldId': 'priority', 'value': priority.value},
                ],
            },
        }

        self._log_payload(UPDATE_CARD_FIELDS_MUTATION, variables)
