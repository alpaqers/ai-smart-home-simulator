from dataclasses import dataclass
import os

#dodatkowy config zeby kod dalo sie uruchomic na roznych systemach
@dataclass(frozen=True)
class ServerConfig:
    host: str = os.getenv("SERVER_HOST", "127.0.0.1")
    port: int = int(os.getenv("SERVER_PORT", "8888"))
    #tutaj w przyszlosci bedzie dodana obsluga ramki pakietu
    buffer_size: int = int(os.getenv("SERVER_BUFFER_SIZE", "1024"))


config = ServerConfig()