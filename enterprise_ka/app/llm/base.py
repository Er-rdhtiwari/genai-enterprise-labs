from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    async def generate(self, system: str, user: str) -> str:
        raise NotImplementedError

class Embedder(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError
