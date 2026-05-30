from fastapi import APIRouter
from fastapi import status

from app.api.deps import ClientServiceDep
from app.schemas.client import ClientCreate
from app.schemas.client import ClientOut

router = APIRouter(prefix='/clients', tags=['clients'])


@router.post('', response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, service: ClientServiceDep) -> ClientOut:
    client = service.create(payload)

    return ClientOut.model_validate(client)
