from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ClientNotFound
from app.integrations.pipefy.base import PipefyClient
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.repositories.event_repository import EventRepository
from app.schemas.client import ClientStatus, Priority
from app.schemas.webhook import CardUpdatedEvent
from app.services.webhook_service import WebhookService


class TestWebhookService:
    @pytest.fixture
    def client_repository(self) -> MagicMock:
        return MagicMock(spec=ClientRepository)

    @pytest.fixture
    def event(self) -> CardUpdatedEvent:
        return CardUpdatedEvent.model_validate(
            {
                'card_id': 'card_1',
                'cliente_email': 'user@example.com',
                'event_id': 'evt_1',
                'timestamp': '2026-05-18T12:00:00Z',
            }
        )

    @pytest.fixture
    def event_repository(self) -> MagicMock:
        return MagicMock(spec=EventRepository)

    @pytest.fixture
    def pipefy_client(self) -> MagicMock:
        return MagicMock(spec=PipefyClient)

    @pytest.fixture
    def service(
        self, client_repository: MagicMock, event_repository: MagicMock, pipefy_client: MagicMock
    ) -> WebhookService:
        return WebhookService(
            client_repository=client_repository,
            event_repository=event_repository,
            pipefy_client=pipefy_client,
        )

    def test_when_event_is_duplicated_ignores_processing(
        self,
        client_repository: MagicMock,
        event: CardUpdatedEvent,
        event_repository: MagicMock,
        pipefy_client: MagicMock,
        service: WebhookService,
    ):
        event_repository.exists.return_value = True

        result = service.process(event)

        assert result.reason == 'duplicated event'
        assert result.status == 'ignored'

        client_repository.commit.assert_not_called()
        client_repository.get_by_email.assert_not_called()

        event_repository.add.assert_not_called()

        pipefy_client.mark_card_as_processed.assert_not_called()

    def test_when_client_does_not_exist_raises_client_not_found(
        self,
        client_repository: MagicMock,
        event: CardUpdatedEvent,
        event_repository: MagicMock,
        pipefy_client: MagicMock,
        service: WebhookService,
    ) -> None:
        event_repository.exists.return_value = False

        client_repository.get_by_email.return_value = None

        with pytest.raises(ClientNotFound) as exc_info:
            service.process(event)

        assert exc_info.value.email == 'user@example.com'

        client_repository.commit.assert_not_called()

        event_repository.add.assert_not_called()

        pipefy_client.mark_card_as_processed.assert_not_called()

    @pytest.mark.parametrize(
        ('patrimony', 'expected_priority'),
        [
            (250000, Priority.HIGH),
            (150000, Priority.NORMAL),
        ],
    )
    def test_when_event_is_new_processes_card_with_correct_priority(
        self,
        client_repository: MagicMock,
        event: CardUpdatedEvent,
        event_repository: MagicMock,
        expected_priority: Priority,
        patrimony: float,
        pipefy_client: MagicMock,
        service: WebhookService,
    ) -> None:
        existing = Client(
            card_id='card_1',
            email='user@example.com',
            name='João',
            patrimony=patrimony,
            request_type='Atualização cadastral',
            status=ClientStatus.AWAITING_REVIEW.value,
        )

        event_repository.exists.return_value = False

        client_repository.get_by_email.return_value = existing

        result = service.process(event)

        assert result.status == 'processed'

        assert existing.status == ClientStatus.PROCESSED.value
        assert existing.priority == expected_priority.value

        client_repository.commit.assert_called_once()

        event_repository.add.assert_called_once()

        pipefy_client.mark_card_as_processed.assert_called_once_with(
            card_id='card_1',
            priority=expected_priority,
        )
