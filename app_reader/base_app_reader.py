from abc import ABCMeta, abstractmethod
from typing import Dict
from PIL import Image


class BaseAppReader(metaclass=ABCMeta):
    @abstractmethod
    def can_read(self, snip_image: Image.Image) -> bool:
        pass

    @abstractmethod
    def read(self, snip_image: Image.Image) -> Dict[str, int]:
        pass
