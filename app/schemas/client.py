from enum import Enum

from pydantic import EmailStr
from pydantic import Field

from app.schemas.base import BaseSchema


class ClientStatus(str, Enum):
    AWAITING_REVIEW = 'Aguardando Análise'
    PROCESSED = 'Processado'


class Priority(str, Enum):
    HIGH = 'Alta'
    NORMAL = 'Normal'


class ClientCreate(BaseSchema):
    model_config = {'populate_by_name': True}

    email: EmailStr = Field(alias='cliente_email')
    name: str = Field(alias='cliente_nome', min_length=1)
    patrimony: float = Field(alias='valor_patrimonio', ge=0)
    request_type: str = Field(alias='tipo_solicitacao', min_length=1)


class ClientOut(BaseSchema):
    card_id: str | None
    email: EmailStr
    id: int
    name: str
    patrimony: float
    priority: Priority | None
    request_type: str
    status: ClientStatus
