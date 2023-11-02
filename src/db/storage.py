from typing import Any
from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def get_instance(self) -> Any:
        pass

    def close_instance(self) -> None:
        pass
