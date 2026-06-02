from app.core.exceptions import ClientNotFound
from app.integrations.pipefy.client import PipefyClient
from app.models.processed_event import ProcessedEvent
from app.repositories.client_repository import ClientRepository
from app.repositories.event_repository import EventRepository
from app.schemas.client import ClientStatus
from app.schemas.client import Priority
from app.schemas.webhook import CardUpdatedEvent
from app.schemas.webhook import WebhookResult

PRIORITY_THRESHOLD: float = 200_000


class WebhookService:
    def __init__(
        self,
        client_repository: ClientRepository,
        event_repository: EventRepository,
        pipefy_client: PipefyClient,
    ) -> None:
        self.client_repository = client_repository
        self.event_repository = event_repository
        self.pipefy_client = pipefy_client

    @staticmethod
    def _resolve_priority(patrimony: float) -> Priority:
        return Priority.HIGH if patrimony >= PRIORITY_THRESHOLD else Priority.NORMAL

    def process(self, event: CardUpdatedEvent) -> WebhookResult:
        if self.event_repository.exists(event.event_id):
            return WebhookResult(status='ignored', reason='duplicated event')

        client = self.client_repository.get_by_email(event.client_email)

        if client is None:
            raise ClientNotFound(event.client_email)

        priority = self._resolve_priority(client.patrimony)

        self.pipefy_client.mark_card_as_processed(
            card_id=event.card_id,
            priority=priority,
        )

        client.status = ClientStatus.PROCESSED.value
        client.priority = priority.value

        self.event_repository.add(ProcessedEvent(event_id=event.event_id))
        self.client_repository.commit()

        return WebhookResult(status='processed')
