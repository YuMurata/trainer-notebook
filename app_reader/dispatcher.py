from abc import ABCMeta, abstractmethod
from exception import InvalidValueException
from typing import Callable


class BaseDispatched(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def init_item(self):
        pass

    @abstractmethod
    def update_current(self, item: object):
        pass

    @abstractmethod
    def __ne__(self, o: object) -> bool:
        pass

    @abstractmethod
    def update_old(self, current_item: object):
        pass

    @abstractmethod
    def copy(self):
        pass


class Dispatcher:
    def __init__(self, callback: Callable[[], None]):
        self.current_item: BaseDispatched = None
        self.old_item: BaseDispatched = None
        self.callback = callback

    def update_item(self, item: BaseDispatched):
        if not self.current_item:
            self.current_item = item.copy()

        self.current_item.update_current(item.copy())
        if not self.old_item or self.current_item != self.old_item:
            self.callback()

        if not self.old_item:
            self.old_item = item.copy()

        self.old_item.update_old(self.current_item)

    def init_item(self):
        if not (self.current_item and self.old_item):
            raise InvalidValueException('item is None')
        self.current_item.init_item()
        self.old_item.init_item()
