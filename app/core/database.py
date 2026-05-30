from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


class Database:
    def __init__(self, database_url: str) -> None:
        self.engine: Engine = create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            future=True,
        )

        self.session_factory: sessionmaker[Session] = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
        )

    def get_session(self) -> Generator[Session, None, None]:
        session: Session = self.session_factory()

        try:
            yield session
        finally:
            session.close()


db: Database = Database(settings.database_url)
get_db = db.get_session
