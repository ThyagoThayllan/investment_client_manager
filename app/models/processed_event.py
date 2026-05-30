from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class ProcessedEvent(Base):
    __tablename__ = 'processed_events'

    event_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
        unique=True,
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
