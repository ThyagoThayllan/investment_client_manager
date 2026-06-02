import requests
from abc import ABC
from abc import abstractmethod

from app.core.config import settings
from app.models.client import Client


class PipefyBase(ABC):
    PIPEFY_API_URL = 'https://api.pipefy.com/graphql'

    def _post(self, mutation: str, variables: dict) -> dict:
        payload = {'query': mutation.strip(), 'variables': variables}

        response = requests.post(
            self.PIPEFY_API_URL,
            headers={'Authorization': f'Bearer {settings.pipefy_token}'},
            json=payload,
        )

        return response.json()

    @abstractmethod
    def create_card(self, client: Client) -> str: ...
