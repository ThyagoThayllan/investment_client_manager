from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class Client(Base):
    __tablename__ = 'clients'

    card_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False, unique=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    patrimony: Mapped[float] = mapped_column(nullable=False)

    priority: Mapped[str | None] = mapped_column(String(50), nullable=True)

    request_type: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False)
