from enum import IntEnum, auto
from uma_info import UmaInfo
from typing import List
from exception import InvalidValueException


class SortKey(IntEnum):
    NAME = 2
    RANKMEAN = auto()
    MAX = auto()
    MIN = auto()
    MEAN = auto()
    STD = auto()


class SortUmaInfo:
    def __init__(self, key_list: List[str]):
        if len(key_list) <= 0:
            raise InvalidValueException('key_list is invalid')

        self.sort_key = key_list[0]
        self.is_reverse = False
        self.key_list = key_list

    def sort(self, uma_info: UmaInfo):
        return uma_info[UmaInfo.item_name_list[int(self.key)-2]]

    def set_key(self, x: int):
        key = SortKey(x)
        if key == SortKey.NUM:
            return

        if key == self.key:
            self.is_reverse = not self.is_reverse
        else:
            self.is_reverse = False

        self.key = key

    @property
    def key_to_str(self):
        return self.key_dict[self.key]
