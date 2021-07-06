from logger import CustomLogger
from TeamStadiumInfoDetection.dispatcher import BaseDispatched, Dispatcher
from TeamStadiumInfoDetection.linked_reader import LinkedReader
from threading import Event,  Lock
from snip import ImageSnipper, DebugSnipperType
from TeamStadiumInfoDetection.rank import RankReader
from TeamStadiumInfoDetection.score import ScoreReader
from typing import Dict, Tuple
from time import sleep
from PIL import Image
from copy import deepcopy
from .thread_closer import StoppableThread


logger = CustomLogger(__name__)


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


class AppLinkedThread(StoppableThread):
    def __init__(self, dispatcher: Dispatcher) -> None:
        super().__init__(name='AppLinkedThread')

        self.snipper = ImageSnipper()
        self.snipper = DebugSnipperType.Race.value(__name__)
        self.lock = Lock()
        self.dispatcher = dispatcher
        self.is_update = True
        self.linked_dict = dict()
        self.reader_dict: Dict[str, LinkedReader] = {
            'rank': RankReader(), 'score': ScoreReader()}
        self.event = Event()

    def stop(self):
        self.is_update = False
        self.event.set()

    def run(self) -> None:
        def each_read(snip_image: Image.Image) -> Tuple[str, Dict[str, int]]:
            for key, reader in self.reader_dict.items():
                if reader.can_read(snip_image):
                    return key, reader.read(snip_image)
            return None

        while self.is_update:
            self.event.wait()
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

    def start(self) -> None:
        self.activate()
        return super().start()

    def get(self) -> Dict[str, Dict[str, int]]:
        with self.lock:
            return self.linked_dict

    def init_dict(self):
        with self.lock:
            self.linked_dict = dict()
            self.dispatcher.update_item(
                LinkedDispatched(self.linked_dict))

    def activate(self):
        self.event.set()

    def deactivate(self):
        self.event.clear()
