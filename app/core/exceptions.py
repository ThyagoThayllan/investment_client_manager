class ClientNotFound(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f'Client with email "{email}" was not found.')
        self.email: str = email


class DuplicatedClient(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f'Client with email "{email}" already exists.')
        self.email: str = email
