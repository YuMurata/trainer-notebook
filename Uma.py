from collections import UserDict
import numpy as np
from pathlib import Path
from exception import FileNotFoundException, InvalidKeyException
import json

from typing import List


class UmaInfo:
    metrics_name_list = ['Max', 'Min', 'Mean', 'Std']
    item_name_list = ['Name'] + metrics_name_list

    def __init__(self, name: str, points: list):
        self.name = name
        self.points = points

    @property
    def Max(self) -> int:
        points = np.array(self.points)
        if np.any(points > 0):
            return int(np.max(points[points > 0]))
        return 0

    @property
    def Min(self) -> int:
        points = np.array(self.points)
        if np.any(points > 0):
            return int(np.min(points[points > 0]))
        return 0

    @property
    def Mean(self) -> int:
        points = np.array(self.points)
        if np.any(points > 0):
            return int(np.mean(points[points > 0]))
        return 0

    @property
    def Std(self) -> int:
        points = np.array(self.points)
        if np.any(points > 0):
            return int(np.std(points[points > 0]))
        return 0

    @property
    def NumRace(self) -> int:
        points = np.array(self.points)
        return np.count_nonzero(points > 0)

    def AddPoint(self, point: int):
        self.points.append(point)

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

    @staticmethod
    def Read() -> UmaInfoDict:
        try:
            if not Path(UmaPointFileIO.resource_path).exists():
                raise FileNotFoundException(
                    f"can't load {UmaPointFileIO.resource_path}")

            with open(UmaPointFileIO.resource_path, 'r', encoding="utf-8_sig") as f:
                return UmaInfoDict([UmaInfo(name, points)
                                    for name, points in json.load(f).items()])
        except:
            return UmaInfoDict()

    @staticmethod
    def Write(uma_info_dict: UmaInfoDict):
        with open(UmaPointFileIO.resource_path, 'w', encoding="utf-8_sig") as f:
            json.dump(
                {uma_info.name: uma_info.points
                 for uma_info in uma_info_dict.values()}, f, indent=2,
                ensure_ascii=False)


class UmaNameFileReader:
    resource_path = './resource/uma_name_list.txt'

    @staticmethod
    def Read() -> list:
        if not Path(UmaNameFileReader.resource_path).exists():
            raise FileNotFoundException(
                f"can't load {UmaNameFileReader.resource_path}")
        with open(UmaNameFileReader.resource_path, 'r', encoding="utf-8_sig") as f:
            return f.readlines()
