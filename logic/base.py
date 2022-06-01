from abc import ABC, abstractmethod


class BaseObject(ABC):
    x: int
    y: int
    @abstractmethod
    def interact(self, other: "BaseObject"):
        pass

    @abstractmethod
    def get_next_action(self):
        pass
