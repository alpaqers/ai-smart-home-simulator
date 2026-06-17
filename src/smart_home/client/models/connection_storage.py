from dataclasses import dataclass, field
from ..controllers.connection_handler import ConnectionHandler

@dataclass
class ConnectionStorage:
    connections: dict[int, ConnectionHandler] = field(default_factory=dict)