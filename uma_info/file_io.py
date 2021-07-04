from pathlib import Path
from exception import FileNotFoundException
import json
from threading import Lock
from .uma_info import UmaInfoDict, UmaInfo, MetricList
from .define import info_data_path, uma_name_path


class UmaPointFileIO:
    lock = Lock()

    @staticmethod
    def Read() -> UmaInfoDict:
        with UmaPointFileIO.lock:
            try:
                if not Path(info_data_path).exists():
                    raise FileNotFoundException(
                        f"can't load {str(info_data_path)}")

                with open(info_data_path, 'r',
                          encoding="utf-8_sig") as f:
                    return UmaInfoDict(
                        [UmaInfo(name, MetricList(info['score']),
                         MetricList(info['rank']))
                         for name, info in json.load(f).items()])
            except (FileNotFoundException, TypeError):
                return UmaInfoDict()

    @staticmethod
    def Write(uma_info_dict: UmaInfoDict):
        with UmaPointFileIO.lock:
            with open(info_data_path, 'w',
                      encoding="utf-8_sig") as f:
                json.dump(
                    {uma_info.name: {'score': uma_info.scores,
                                     'rank': uma_info.ranks}
                     for uma_info in uma_info_dict.values()}, f, indent=2,
                    ensure_ascii=False)


class UmaNameFileReader:
    lock = Lock()

    @ staticmethod
    def Read() -> list:
        with UmaNameFileReader.lock:
            if not Path(uma_name_path).exists():
                raise FileNotFoundException(
                    f"can't load {str(uma_name_path)}")
            with open(uma_name_path, 'r',
                      encoding="utf-8_sig") as f:
                return [uma_name.replace('\n', '')
                        for uma_name in f.readlines()]
