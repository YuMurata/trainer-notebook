from logger import init_logger
from TeamStadiumInfoDetection.dispatcher import BaseDispatched, Dispatcher
from TeamStadiumInfoDetection.linked_reader import LinkedReader
from threading import Thread, Lock
from snip import ImageSnipper, DebugSnipperType
from TeamStadiumInfoDetection.rank import RankReader
from TeamStadiumInfoDetection.score import ScoreReader
from typing import Dict, Tuple
from time import sleep
from PIL import Image
from copy import deepcopy
from Uma import UmaPointFileIO
import threading
logger = init_logger(__name__)


class LinkedDispatched(BaseDispatched):
    def __init__(self, linked_dict: Dict[str, Dict[str, int]]) -> None:
        self.linked_dict = deepcopy(linked_dict)

    def update_current(self, item: object):
        self.linked_dict.update(item.linked_dict)

    def update_old(self, current_item: object):
        self.linked_dict = deepcopy(current_item.linked_dict)

    def __ne__(self, o: object) -> bool:
        if type(self) != type(o):
            return False
        return self.linked_dict != o.linked_dict

    def init_item(self):
        self.linked_dict = dict()

    def copy(self):
        return LinkedDispatched(self.linked_dict)


class AppLinkedThread(Thread):
    def __init__(self, dispatcher: Dispatcher) -> None:
        super().__init__(name='AppLinkedThread')

        self.snipper = ImageSnipper()
        self.snipper = DebugSnipperType.RaceScore.value(__name__)
        self.lock = Lock()
        self.dispatcher = dispatcher
        self.is_update = True
        self.linked_dict = dict()
        self.reader_dict: Dict[str, LinkedReader] = {
            'rank': RankReader(), 'score': ScoreReader()}

    def stop(self):
        self.is_update = False

    def run(self) -> None:
        def each_read(snip_image: Image.Image) -> Tuple[str, Dict[str, int]]:
            for key, reader in self.reader_dict.items():
                if reader.can_read(snip_image):
                    return key, reader.read(snip_image)
            return None

        while self.is_update:
            if not threading.main_thread().is_alive():
                return

            snip_image = self.snipper.Snip()
            if snip_image:
                read_item = each_read(snip_image)
                if read_item:
                    key = read_item[0]
                    read_dict = read_item[1]

                    with self.lock:
                        for name in read_dict.keys():
                            self.linked_dict.setdefault(name, dict())
                            self.linked_dict[name][key] = read_dict[name]
                        self.dispatcher.update_item(
                            LinkedDispatched(self.linked_dict))

            sleep(0.1)

    def get(self) -> Dict[str, Dict[str, int]]:
        with self.lock:
            return self.linked_dict

    def init_dict(self):
        with self.lock:
            self.linked_dict = dict()
            self.dispatcher.update_item(
                LinkedDispatched(self.linked_dict))

    def overwrite_umainfo_file(self):
        uma_info_dict = UmaPointFileIO.Read()

        with self.lock:
            for name, info in self.linked_dict.items():
                score = info['score']
                rank = info['rank']
                uma_info_dict[name].add_score(score)
                uma_info_dict[name].add_rank(rank)

        UmaPointFileIO.Write(uma_info_dict)
