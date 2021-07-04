from collections import UserDict
import numpy as np
from pathlib import Path
from exception import FileNotFoundException, InvalidKeyException
import json
from threading import Lock
from typing import List


class UmaInfo:
    metrics_name_list = ['RankMean', 'Max', 'Min', 'Mean', 'Std']
    item_name_list = ['Name'] + metrics_name_list

    def __init__(self, name: str, scores: List[int], ranks: List[int]):
        self.name = name
        self.scores = scores
        self.ranks = ranks

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, UmaInfo):
            return False
        return self.__hash__() == o.__hash__()

    def __hash__(self) -> int:
        return hash(f'{self.name}{self.scores}')

    @property
    def Max(self) -> int:
        points = np.array(self.scores)
        if np.any(points > 0):
            return int(np.max(points[points > 0]))
        return 0

    @property
    def Min(self) -> int:
        points = np.array(self.scores)
        if np.any(points > 0):
            return int(np.min(points[points > 0]))
        return 0

    @property
    def Mean(self) -> int:
        points = np.array(self.scores)
        if np.any(points > 0):
            return int(np.mean(points[points > 0]))
        return 0

    @property
    def Std(self) -> int:
        points = np.array(self.scores)
        if np.any(points > 0):
            return int(np.std(points[points > 0]))
        return 0

    @property
    def RankMean(self) -> float:
        ranks = np.array(self.ranks)
        if np.any(ranks > 0):
            return np.mean(ranks[ranks > 0])
        return 0

    @property
    def NumRace(self) -> int:
        points = np.array(self.scores)
        return np.count_nonzero(points > 0)

    def add_score(self, score: int):
        self.scores.append(score)

    def add_rank(self, rank: int):
        self.ranks.append(rank)

    def __getitem__(self, key: str):
        item_list = ['Name'] + self.metrics_name_list
        if key not in item_list:
            raise InvalidKeyException(f'{key} is not metrics')

        return {name: metrics
                for name, metrics in zip(item_list, [self.name, self.RankMean,
                                                     self.Max,
                                                     self.Min, self.Mean,
                                                     self.Std])}[key]


class UmaInfoDict(UserDict):
    def __init__(self, __list: List[UmaInfo] = None) -> None:
        __dict = {uma_info.name: uma_info
                  for uma_info in __list} if __list else None
        super().__init__(__dict)

    def add(self, uma_info: UmaInfo):
        self.data[uma_info.name] = uma_info

    def __getitem__(self, key: str) -> UmaInfo:
        if key not in self.data:
            self.add(UmaInfo(key, [], []))
        return self.data[key]


unko
