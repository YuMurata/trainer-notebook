from enum import IntEnum, auto
from .uma_info import MetricList, UmaInfo
from typing import List
from exception import InvalidValueException
from logger import CustomLogger
logger = CustomLogger(__name__)


class SortKey(IntEnum):
    RANKMEAN = auto()
    MAX = auto()
    MIN = auto()
    MEAN = auto()
    STD = auto()


class SortUmaInfo:
    def __init__(self):
        self.key_list = tuple(['name'])+MetricList.metrics_name_list
        self.sort_key = self.key_list[0]
        logger.debug(self.key_list)
        self.is_reverse = False

    def sort(self, uma_info: UmaInfo):
        ret_dict = dict(
            name=uma_info.name,
            max=uma_info.scores.max,
            min=uma_info.scores.min,
            mean=uma_info.scores.mean,
            std=uma_info.scores.std)

        return ret_dict[self.sort_key]

    def set_key(self, key: str):
        logger.debug(f'key: {key}')
        if key not in self.key_list:
            raise InvalidValueException('invalid key')

        if key == self.sort_key:
            self.is_reverse = not self.is_reverse
        else:
            self.is_reverse = False

        self.sort_key = key

    def set_key_index(self, key_index: int):
        is_within_range = 0 <= key_index < len(self.key_list)
        if not is_within_range:
            raise InvalidValueException('invalid key index')

        self.set_key(self.key_list[key_index])

    @ property
    def key_to_str(self):
        return self.key_dict[self.key]
