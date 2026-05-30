from sqlalchemy import select

from app.models.processed_event import ProcessedEvent
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[ProcessedEvent]):
    model = ProcessedEvent

    def exists(self, event_id: str) -> bool:
        statement = select(ProcessedEvent.id).where(ProcessedEvent.event_id == event_id)

        return self.session.scalars(statement).first() is not None
