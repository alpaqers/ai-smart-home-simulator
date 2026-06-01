from ..models.connection_storage import ConnectionStorage
from ..controllers.connection_handler import ConnectionHandler


def add_connection(storage: ConnectionStorage, device_id: int, handler: ConnectionHandler) -> None:
    storage.connections[device_id] = handler

def get_connection(storage: ConnectionStorage, device_id: int) -> ConnectionHandler | None:
    return storage.connections.get(device_id)

def remove_connection(storage: ConnectionStorage, device_id: int) -> None:
    storage.connections.pop(device_id, None)

def all_connections(storage: ConnectionStorage) -> list[ConnectionHandler]:
    return list(storage.connections.values())