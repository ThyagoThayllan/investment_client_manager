import logging

from app.integrations.pipefy.base import PipefyBase
from app.integrations.pipefy.mutations import CREATE_CARD_MUTATION
from app.integrations.pipefy.mutations import UPDATE_CARD_FIELDS_MUTATION
from app.models.client import Client
from app.schemas.client import ClientStatus
from app.schemas.client import Priority

logger = logging.getLogger(__name__)


class PipefyClient(PipefyBase):
    # NOTE: Your pipe id in Pipefy, you can get it from your pipe URL, e.g.:
    #       https://app.pipefy.com/pipes/123 -> PIPE_ID = 123
    PIPE_ID: int = 0

    def create_card(self, client: Client) -> str:
        variables = {
            'input': {
                'pipe_id': self.PIPE_ID,
                'fields_attributes': [
                    {'field_id': 'email', 'field_value': client.email},
                    {'field_id': 'nome_do_cliente', 'field_value': client.name},
                    {'field_id': 'patrim_nio', 'field_value': client.patrimony},
                    {'field_id': 'status', 'field_value': client.status},
                ],
            },
        }

        data = self._post(CREATE_CARD_MUTATION, variables)

        card_id: str = data['data']['createCard']['card']['id']

        logger.info('Pipefy card created: %s', card_id)

        return card_id

    def mark_card_as_processed(self, card_id: str, priority: Priority) -> None:
        variables: dict[str, object] = {
            'input': {
                'nodeId': card_id,
                'values': [
                    {'fieldId': 'status', 'value': ClientStatus.PROCESSED.value},
                    {'fieldId': 'prioridade', 'value': priority.value},
                ],
            },
        }

        self._post(UPDATE_CARD_FIELDS_MUTATION, variables)

        logger.info('Pipefy card marked as processed: %s', card_id)
