from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from app.api.deps import ClientServiceDep
from app.core.exceptions import DuplicatedClient
from app.schemas.client import ClientCreate
from app.schemas.client import ClientOut

router = APIRouter(prefix='/clients', tags=['clients'])


@router.post('', response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, service: ClientServiceDep) -> ClientOut:
    try:
        client = service.create(payload)
    except DuplicatedClient as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return ClientOut.model_validate(client)
