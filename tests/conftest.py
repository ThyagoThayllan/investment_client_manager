from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_pipefy_client
from app.core.database import get_db
from app.integrations.pipefy.client import PipefyClient
from app.main import app
from app.models.base import Base


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def mock_pipefy_client() -> MagicMock:
    mock = MagicMock(spec=PipefyClient)
    mock.create_card.return_value = 'card_fake_123'
    return mock


@pytest.fixture
def client(db_session: Session, mock_pipefy_client: MagicMock) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_pipefy_client] = lambda: mock_pipefy_client

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
