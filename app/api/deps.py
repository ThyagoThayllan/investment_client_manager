from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.pipefy.base import PipefyClient
from app.integrations.pipefy.client import FakePipefyClient
from app.repositories.client_repository import ClientRepository
from app.repositories.event_repository import EventRepository
from app.services.client_service import ClientService
from app.services.webhook_service import WebhookService

SessionDep = Annotated[Session, Depends(get_db)]


def get_pipefy_client() -> PipefyClient:
    return FakePipefyClient()


PipefyClientDep = Annotated[PipefyClient, Depends(get_pipefy_client)]


def get_client_service(pipefy_client: PipefyClientDep, session: SessionDep) -> ClientService:
    return ClientService(pipefy_client=pipefy_client, repository=ClientRepository(session))


def get_webhook_service(pipefy_client: PipefyClientDep, session: SessionDep) -> WebhookService:
    return WebhookService(
        client_repository=ClientRepository(session),
        event_repository=EventRepository(session),
        pipefy_client=pipefy_client,
    )


ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]
WebhookServiceDep = Annotated[WebhookService, Depends(get_webhook_service)]
