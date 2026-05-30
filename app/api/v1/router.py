from fastapi import APIRouter

from app.api.v1.endpoints import clients
from app.api.v1.endpoints import webhooks

api_router = APIRouter()
api_router.include_router(clients.router)
api_router.include_router(webhooks.router)
