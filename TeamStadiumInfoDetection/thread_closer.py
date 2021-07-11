from abc import ABCMeta, abstractmethod
from threading import Thread
import threading
from typing import List
from time import sleep


class StoppableThread(Thread, metaclass=ABCMeta):
    @abstractmethod
    def stop(self):
        raise NotImplementedError('stop not impl')


class ThreadCloser(Thread):
    def __init__(self, thread_list: List[StoppableThread]) -> None:
        super().__init__(name='ThreadCloser')
        self.thread_list = thread_list
        self.sleep_time = 1

    def run(self) -> None:
        while threading.main_thread().is_alive():
            sleep(self.sleep_time)

        for thread in self.thread_list:
            thread.stop()
