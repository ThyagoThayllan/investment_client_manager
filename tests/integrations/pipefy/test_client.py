import json
import logging

import pytest
from _pytest.logging import LogCaptureFixture

from app.integrations.pipefy.client import FakePipefyClient
from app.models.client import Client
from app.schemas.client import ClientStatus, Priority


class TestFakePipefyClient:
    LOGGER_NAME = 'app.integrations.pipefy.client'

    @pytest.fixture
    def pipefy(self) -> FakePipefyClient:
        return FakePipefyClient()

    @pytest.fixture
    def sample_client(self) -> Client:
        return Client(
            name='João',
            email='joao@example.com',
            request_type='Atualização cadastral',
            patrimony=250000,
            status=ClientStatus.AWAITING_REVIEW.value,
        )

    @staticmethod
    def _captured_payload(caplog: LogCaptureFixture) -> dict[str, object]:
        record = next(
            r for r in caplog.records if 'Pipefy GraphQL payload' in r.getMessage()
        )
        raw = record.getMessage().split('Pipefy GraphQL payload: ', 1)[1]
        return json.loads(raw)

    def test_when_creating_card_logs_payload_with_correct_structure(
        self,
        pipefy: FakePipefyClient,
        sample_client: Client,
        caplog: LogCaptureFixture,
    ) -> None:
        with caplog.at_level(logging.INFO, logger=self.LOGGER_NAME):
            card_id = pipefy.create_card(sample_client)

        payload = self._captured_payload(caplog)
        assert 'createCard' in payload['query']
        assert 'CreateCardInput!' in payload['query']
        assert payload['variables']['input']['pipe_id'] == 'FAKE_PIPE_ID'

        fields = payload['variables']['input']['fields_attributes']
        assert {'field_id': 'cliente_nome', 'field_value': 'João'} in fields
        assert {'field_id': 'cliente_email', 'field_value': 'joao@example.com'} in fields
        assert card_id.startswith('card_fake_')

    def test_when_marking_card_as_processed_logs_payload_with_status_and_priority(
        self,
        pipefy: FakePipefyClient,
        caplog: LogCaptureFixture,
    ) -> None:
        with caplog.at_level(logging.INFO, logger=self.LOGGER_NAME):
            pipefy.mark_card_as_processed(card_id='card_456', priority=Priority.HIGH)

        payload = self._captured_payload(caplog)
        assert 'updateFieldsValues' in payload['query']
        assert 'UpdateFieldsValuesInput!' in payload['query']
        assert payload['variables']['input']['nodeId'] == 'card_456'

        values = payload['variables']['input']['values']
        assert {'fieldId': 'status', 'value': 'Processado'} in values
        assert {'fieldId': 'priority', 'value': 'prioridade_alta'} in values
