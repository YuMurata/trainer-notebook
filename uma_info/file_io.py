from logger import CustomLogger
from pathlib import Path
from exception import FileNotFoundException
import json
from threading import Lock
from .uma_info import UmaInfoDict, UmaInfo, MetricList
from .define import info_data_path, uma_name_path

logger = CustomLogger(__name__)


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
            except json.decoder.JSONDecodeError as e:
                logger.warning(str(e))
                return UmaInfoDict()

    @staticmethod
    def Write(uma_info_dict: UmaInfoDict):
        with UmaPointFileIO.lock:
            with open(info_data_path, 'w',
                      encoding="utf-8_sig") as f:
                a = uma_info_dict.to_list()[0]
                logger.debug(f'{a.name}: {a.scores}')
                json.dump(
                    {uma_info.name: {'score': uma_info.scores.to_list(),
                                     'rank': uma_info.ranks.to_list()}
                     for uma_info in uma_info_dict.to_list()}, f, indent=2,
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
