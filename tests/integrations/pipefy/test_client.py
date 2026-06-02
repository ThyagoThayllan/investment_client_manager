from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.integrations.pipefy.client import PipefyClient
from app.models.client import Client
from app.schemas.client import ClientStatus, Priority


class TestPipefyClient:
    @pytest.fixture
    def pipefy(self) -> PipefyClient:
        return PipefyClient()

    @pytest.fixture
    def sample_client(self) -> Client:
        return Client(
            name='João',
            email='joao@example.com',
            request_type='Atualização cadastral',
            patrimony=250000,
            status=ClientStatus.AWAITING_REVIEW.value,
        )

    def test_create_card_returns_card_id(
        self,
        pipefy: PipefyClient,
        sample_client: Client,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'createCard': {'card': {'id': 'card_123'}}}}

        with patch('app.integrations.pipefy.base.requests.post', return_value=mock_response) as mock_post:
            card_id = pipefy.create_card(sample_client)

        assert card_id == 'card_123'
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        fields = kwargs['json']['variables']['input']['fields_attributes']
        assert {'field_id': 'nome_do_cliente', 'field_value': 'João'} in fields
        assert {'field_id': 'email', 'field_value': 'joao@example.com'} in fields

    def test_create_card_sends_correct_mutation(
        self,
        pipefy: PipefyClient,
        sample_client: Client,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'createCard': {'card': {'id': 'card_456'}}}}

        with patch('app.integrations.pipefy.base.requests.post', return_value=mock_response) as mock_post:
            pipefy.create_card(sample_client)

        _, kwargs = mock_post.call_args
        assert 'createCard' in kwargs['json']['query']
        assert 'CreateCardInput!' in kwargs['json']['query']

    def test_mark_card_as_processed_sends_correct_mutation(
        self,
        pipefy: PipefyClient,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'updateFieldsValues': {'success': True}}}

        with patch('app.integrations.pipefy.base.requests.post', return_value=mock_response) as mock_post:
            pipefy.mark_card_as_processed(card_id='card_456', priority=Priority.HIGH)

        _, kwargs = mock_post.call_args
        assert 'updateFieldsValues' in kwargs['json']['query']
        assert 'UpdateFieldsValuesInput!' in kwargs['json']['query']
        variables = kwargs['json']['variables']['input']
        assert variables['nodeId'] == 'card_456'
        values = variables['values']
        assert {'fieldId': 'status', 'value': 'Processado'} in values
        assert {'fieldId': 'prioridade', 'value': 'Alta'} in values
