from sqlalchemy import select

from app.models.client import Client
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    model = Client

    def get_by_email(self, email: str) -> Client | None:
        statement = select(Client).where(Client.email == email)

        return self.session.scalars(statement).first()
