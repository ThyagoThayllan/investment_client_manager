class ClientNotFound(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f'Client with email "{email}" was not found.')
        self.email: str = email


class DuplicateEvent(Exception):
    def __init__(self, event_id: str) -> None:
        super().__init__(f'Event "{event_id}" has already been processed.')
        self.event_id: str = event_id
