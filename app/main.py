import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import db
from app.models.base import Base


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=db.engine)
    yield


def create_app() -> FastAPI:
    logging.basicConfig(level=settings.log_level)

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(api_router)

    return app


app: FastAPI = create_app()
