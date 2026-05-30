from datetime import datetime

from pydantic import EmailStr
from pydantic import Field

from app.schemas.base import BaseSchema


class CardUpdatedEvent(BaseSchema):
    model_config = {'populate_by_name': True}

    card_id: str = Field(min_length=1)
    client_email: EmailStr = Field(alias='cliente_email')
    event_id: str = Field(min_length=1)
    timestamp: datetime


class WebhookResult(BaseSchema):
    reason: str | None = None
    status: str
