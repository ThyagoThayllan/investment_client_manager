import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.client import Client


class TestCreateClientEndpoint:
    @pytest.fixture
    def valid_payload(self) -> dict[str, object]:
        return {
            'cliente_email': 'joao.silva@example.com',
            'cliente_nome': 'João Silva',
            'tipo_solicitacao': 'Atualização cadastral',
            'valor_patrimonio': 250000,
        }

    def test_with_valid_payload(self, client: TestClient, db_session: Session, valid_payload: dict):
        response = client.post('/clients', json=valid_payload)

        assert response.status_code == 201

        body = response.json()
        assert body['card_id'].startswith('card_fake_')
        assert body['email'] == 'joao.silva@example.com'
        assert body['name'] == 'João Silva'
        assert body['priority'] is None
        assert body['status'] == 'Aguardando Análise'

        stored = db_session.query(Client).filter_by(email='joao.silva@example.com').one()
        assert stored.card_id == body['card_id']
        assert stored.status == 'Aguardando Análise'

    def test_with_invalid_payload(self, client: TestClient, valid_payload: dict):
        valid_payload['cliente_email'] = 'invalid_email'

        response = client.post('/clients', json=valid_payload)

        assert response.status_code == 422
