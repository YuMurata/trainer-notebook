from pathlib import Path
from exception import FileNotFoundException
import json
from threading import Lock
from .uma_info import UmaInfoDict, UmaInfo, MetricList


class UmaPointFileIO:
    resource_path = './resource/user/uma_pt_list.json'
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
                    return UmaInfoDict(
                        [UmaInfo(name, info['score'], info['rank'])
                         for name, info in json.load(f).items()])
            except (FileNotFoundException, TypeError):
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
    resource_path = './resource/system/uma_name_list.txt'
    lock = Lock()

    @ staticmethod
    def Read() -> list:
        with UmaNameFileReader.lock:
            if not Path(UmaNameFileReader.resource_path).exists():
                raise FileNotFoundException(
                    f"can't load {UmaNameFileReader.resource_path}")
            with open(UmaNameFileReader.resource_path, 'r',
                      encoding="utf-8_sig") as f:
                return [uma_name.replace('\n', '')
                        for uma_name in f.readlines()]
