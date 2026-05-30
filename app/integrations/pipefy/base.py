from abc import ABC
from abc import abstractmethod

from app.models.client import Client
from app.schemas.client import Priority


class PipefyClient(ABC):
    @abstractmethod
    def create_card(self, client: Client) -> str: ...

    @abstractmethod
    def mark_card_as_processed(self, card_id: str, priority: Priority) -> None: ...
