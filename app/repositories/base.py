from typing import Generic
from typing import TypeVar

from sqlalchemy.orm import Session

from app.models.base import Base

Model = TypeVar('Model', bound=Base)


class BaseRepository(Generic[Model]):
    model: type[Model]

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, model: Model) -> Model:
        self.session.add(model)
        return model

    def commit(self) -> None:
        self.session.commit()

    def get(self, pk: object) -> Model | None:
        return self.session.get(self.model, pk)

    def refresh(self, model: Model) -> None:
        self.session.refresh(model)
