from abc import ABC, abstractmethod


class AbstractProvider(ABC):
    @staticmethod
    @abstractmethod
    def register(server):
        raise NotImplementedError
