from collections import UserDict, UserList
import numpy as np
from typing import Callable, Iterable, List,  Optional


class MetricCalculator:
    @staticmethod
    def _base(value_list: List[int], calc: Callable[[np.ndarray], int]):
        value_array = np.array(value_list)
        if np.any(value_array > 0):
            return int(calc(value_array[value_array > 0]))
        return 0

    @staticmethod
    def max(value_list: List[int]) -> int:
        return MetricCalculator._base(value_list, np.max)

    @staticmethod
    def min(value_list: List[int]) -> int:
        return MetricCalculator._base(value_list, np.min)

    @staticmethod
    def mean(value_list: List[int]) -> int:
        return MetricCalculator._base(value_list, np.mean)

    @staticmethod
    def std(value_list: List[int]) -> int:
        return MetricCalculator._base(value_list, np.std)


class MetricList(UserList):
    def __init__(self, initlist: Optional[Iterable[int]]) -> None:
        super().__init__(initlist=initlist)

    def _base(self, calc: Callable[[np.ndarray], int]) -> int:
        value_array = np.array(self.data)
        if np.any(value_array > 0):
            return int(calc(value_array[value_array > 0]))
        return 0

    @property
    def max(self) -> int:
        return self._base(np.max)

    @property
    def min(self) -> int:
        return self._base(np.min)

    @property
    def mean(self) -> int:
        return self._base(np.mean)

    @property
    def std(self) -> int:
        return self._base(np.std)

    def __getitems__(self, i: int) -> int:
        return self.data[i]


class UmaInfo:
    def __init__(self, name: str, scores: MetricList, ranks: MetricList):
        self.name = name
        self.scores = scores
        self.ranks = ranks

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, UmaInfo):
            return False
        return self.__hash__() == o.__hash__()

    def __hash__(self) -> int:
        return hash(f'{self.name}{self.scores}{self.ranks}')

    def get_num_race(self) -> int:
        score_array = np.array(self.scores)
        rank_array = np.array(self.ranks)
        return max(np.count_nonzero(score_array > 0),
                   np.count_nonzero(rank_array > 0))

    def add_score(self, score: int):
        self.scores.append(score)

    def add_rank(self, rank: int):
        self.ranks.append(rank)


class UmaInfoDict(UserDict):
    def __init__(self, __list: List[UmaInfo] = None) -> None:
        __dict = {uma_info.name: uma_info
                  for uma_info in __list} if __list else None
        super().__init__(__dict)

    def add(self, uma_info: UmaInfo):
        self.data[uma_info.name] = uma_info

    def __getitem__(self, key: str) -> UmaInfo:
        if key not in self.data:
            self.add(UmaInfo(key, MetricList(), MetricList()))
        return self.data[key]
