from app.integrations.pipefy.client import PipefyClient
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate
from app.schemas.client import ClientStatus


class ClientService:
    def __init__(
        self,
        pipefy_client: PipefyClient,
        repository: ClientRepository,
    ) -> None:
        self.repository = repository
        self.pipefy_client = pipefy_client

    def create(self, payload: ClientCreate) -> Client:
        client = Client(
            email=payload.email,
            name=payload.name,
            patrimony=payload.patrimony,
            request_type=payload.request_type,
            status=ClientStatus.AWAITING_REVIEW.value,
        )

        self.repository.add(client)

        client.card_id = self.pipefy_client.create_card(client)

        self.repository.commit()
        self.repository.refresh(client)

        return client
