from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from app.api.deps import WebhookServiceDep
from app.core.exceptions import ClientNotFound
from app.schemas.webhook import CardUpdatedEvent
from app.schemas.webhook import WebhookResult

router = APIRouter(prefix='/webhooks/pipefy', tags=['webhooks'])


@router.post('/card-updated', response_model=WebhookResult)
def card_updated(event: CardUpdatedEvent, service: WebhookServiceDep) -> WebhookResult:
    try:
        return service.process(event)
    except ClientNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
