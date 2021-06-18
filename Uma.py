from collections import UserDict
import numpy as np
from pathlib import Path
from exception import FileNotFoundException, InvalidKeyException
import json
from threading import Lock
from typing import List


class UmaInfo:
    metrics_name_list = ['Max', 'Min', 'Mean', 'Std']
    item_name_list = ['Name'] + metrics_name_list

    def __init__(self, name: str, scores: List[int], ranks: List[int]):
        self.name = name
        self.scores = scores

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
    def NumRace(self) -> int:
        points = np.array(self.scores)
        return np.count_nonzero(points > 0)

    def add_score(self, score: int):
        self.scores.append(score)

    def __getitem__(self, key: str):
        item_list = ['Name'] + self.metrics_name_list
        if key not in item_list:
            raise InvalidKeyException(f'{key} is not metrics')

        return {name: metrics
                for name, metrics in zip(item_list, [self.name, self.Max,
                                                     self.Min, self.Mean,
                                                     self.Std])}[key]


class UmaInfoDict(UserDict):
    def __init__(self, __list: List[UmaInfo] = None) -> None:
        __dict = {uma_info.name: uma_info
                  for uma_info in __list} if __list is not None else None
        super().__init__(__dict)

    def add(self, uma_info: UmaInfo):
        self.data[uma_info.name] = uma_info

    def __getitem__(self, key: str) -> UmaInfo:
        if key not in self.data:
            self.add(UmaInfo(key, []))
        return self.data[key]


class UmaPointFileIO:
    resource_path = './resource/uma_pt_list.json'
    lock = Lock()

    @staticmethod
    def Read() -> UmaInfoDict:
        with UmaPointFileIO.lock:
            try:
                if not Path(UmaPointFileIO.resource_path).exists():
                    raise FileNotFoundException(
                        f"can't load {UmaPointFileIO.resource_path}")

                with open(UmaPointFileIO.resource_path, 'r',
                          encoding="utf-8_sig") as f:
            except FileNotFoundException:
                    return UmaInfoDict(
                        [UmaInfo(name, info['score'], info['rank'])
                return UmaInfoDict()

    @staticmethod
    def Write(uma_info_dict: UmaInfoDict):
        with UmaPointFileIO.lock:
            with open(UmaPointFileIO.resource_path, 'w',
                      encoding="utf-8_sig") as f:
                json.dump(
                    {uma_info.name: {'score': uma_info.scores,
                                     'rank': uma_info.ranks}
                     for uma_info in uma_info_dict.values()}, f, indent=2,
                    ensure_ascii=False)


class UmaNameFileReader:
    resource_path = './resource/uma_name_list.txt'
    lock = Lock()

    @staticmethod
    def Read() -> list:
        with UmaNameFileReader.lock:
            if not Path(UmaNameFileReader.resource_path).exists():
                raise FileNotFoundException(
                    f"can't load {UmaNameFileReader.resource_path}")
            with open(UmaNameFileReader.resource_path, 'r',
                      encoding="utf-8_sig") as f:
                return [uma_name.replace('\n', '')
                        for uma_name in f.readlines()]
