import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientStatus


class TestCardUpdatedEndpoint:
    @pytest.fixture
    def existing_client(self, db_session: Session) -> Client:
        client = Client(
            card_id='card_fake_seed',
            email='user@example.com',
            name='João Silva',
            patrimony=250000,
            request_type='Atualização cadastral',
            status=ClientStatus.AWAITING_REVIEW.value,
        )

        db_session.add(client)
        db_session.commit()

        return client

    @pytest.fixture
    def payload(self) -> dict[str, object]:
        return {
            'card_id': 'card_1',
            'cliente_email': 'user@example.com',
            'event_id': 'evt_1',
            'timestamp': '2026-05-18T12:00:00Z',
        }

    @pytest.fixture
    def webhook_url(self) -> str:
        return '/webhooks/pipefy/card-updated'

    @pytest.mark.usefixtures('existing_client')
    def test_when_event_is_new_returns_200_with_processed_status(
        self,
        client: TestClient,
        webhook_url: str,
        payload: dict[str, object],
    ) -> None:
        response = client.post(webhook_url, json=payload)

        assert response.status_code == 200
        assert response.json() == {'status': 'processed', 'reason': None}

    @pytest.mark.usefixtures('existing_client')
    def test_when_event_is_duplicated_returns_200_with_ignored_status(
        self,
        client: TestClient,
        webhook_url: str,
        payload: dict[str, object],
    ) -> None:
        client.post(webhook_url, json=payload)

        response = client.post(webhook_url, json=payload)

        assert response.status_code == 200
        assert response.json() == {'status': 'ignored', 'reason': 'duplicated event'}

    def test_when_client_does_not_exist_returns_404(
        self,
        client: TestClient,
        webhook_url: str,
        payload: dict[str, object],
    ) -> None:
        response = client.post(webhook_url, json=payload)

        assert response.status_code == 404
        assert 'user@example.com' in response.json()['detail']

    def test_when_payload_has_invalid_email_returns_422(
        self,
        client: TestClient,
        webhook_url: str,
        payload: dict[str, object],
    ) -> None:
        payload['cliente_email'] = 'not-an-email'

        response = client.post(webhook_url, json=payload)

        assert response.status_code == 422
