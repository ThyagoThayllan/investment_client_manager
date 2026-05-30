from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        onupdate=func.now(),
        server_default=func.now(),
    )
