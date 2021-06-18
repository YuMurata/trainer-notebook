from threading import Thread, Lock
from typing import Tuple
from Uma import UmaNameFileReader
from snip import ImageSnipper
from misc import concat_imshow, pil2cv
import cv2
from PIL import Image
import time
from pprint import pprint
from pathlib import Path
import numpy as np
from TeamStadiumInfoDetection.dispatcher import BaseDispatched, Dispatcher
from exception import InvalidTypeException


class debugger:
    @staticmethod
    def get_uma_range(uma_loc: Tuple[int, int]) -> Tuple[Tuple[int, int],
                                                         Tuple[int, int]]:
        '''
        Args:
            umaloc (tuple(left, top))
        Returns:
            tuple(tuple(left, top), tuple(right, bottom))
        '''
        return ((uma_loc[0], uma_loc[1]), (uma_loc[0]+40, uma_loc[1]+50))

    @staticmethod
    def get_uma_region(src_region: np.ndarray,
                       uma_loc: Tuple[int, int]) -> np.ndarray:
        ((left, top), (right, bottom)) = debugger.get_uma_range(uma_loc)
        return src_region[top:bottom, left:right]

    @staticmethod
    def show_uma(src_region: np.ndarray, uma_loc: Tuple[int, int],
                 uma_name: str):
        '''
        Args:
            src_region (np.ndarray)
            umaloc (tuple(left, top))
        Returns:
            None
        '''
        cv2.imshow(uma_name, debugger.get_uma_region(src_region, uma_loc))
        cv2.waitKey(0)

    @staticmethod
    def show_detect_and_uma(src_region: np.ndarray, uma_loc: Tuple[int, int],
                            uma_name: str):
        '''
        Args:
            src_region (np.ndarray)
            umaloc (tuple(left, top))
        Returns:
            None
        '''

        left_top, right_bottom = debugger.get_uma_range(uma_loc)
        uma_region = debugger.get_uma_region(src_region, uma_loc)

        detect_region = src_region.copy()
        cv2.rectangle(detect_region, left_top, right_bottom, (0, 0, 255), 3)
        concat_imshow(uma_name, [detect_region, uma_region])
        cv2.waitKey(0)


class RankDispatcher:
    def __init__(self, callback):
        self.init_rank()
        self.callback = callback

    def update_rank(self, rank: dict):
        self.current_rank.update(rank)
        if self.current_rank != self.old_rank:
            self.callback()

        self.old_rank = self.current_rank.copy()

    def init_rank(self):
        self.current_rank = dict()
        self.old_rank = dict()


class RankDispatched(BaseDispatched):
    def __init__(self, score_dict: dict) -> None:
        super().__init__()
        self.rank_dict = score_dict.copy()

    def init_item(self):
        self.rank_dict = dict()

    def update_current(self, item: object):
        if type(item) != type(self):
            raise InvalidTypeException(f'except {str(type(self))}')

        self.rank_dict.update(item.rank_dict)

    def update_old(self, current_item: object):
        self.rank_dict = current_item.rank_dict.copy()

    def __ne__(self, item: object) -> bool:
        if type(item) != type(self):
            return False
        return self.rank_dict != item.rank_dict

    def copy(self):
        return RankDispatched(self.rank_dict)


class RankReadThread(Thread):
    rank_num = 12

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(name='RankReadThread')
        self.snipper = ImageSnipper()
        self.all_uma_name_list = UmaNameFileReader().Read()
        self.lock = Lock()
        self.uma_rank_dict = dict()
        self.dispatcher = dispatcher

        self.template_rank = [cv2.imread(
            f'./resource/rank/rank{i+1:02}.png') for i in range(self.rank_num)]
        self.template_uma_dict = {
            path.stem: pil2cv(Image.open(path))
            for path in Path('./resource/uma_template').iterdir()}

        self.is_update = True

    def stop(self):
        self.is_update = False

    def run(self):
        while self.is_update:
            self._make_uma_rank_dict()
            with self.lock:
                self.dispatcher.update_item(RankDispatched(self.uma_rank_dict))
            time.sleep(0.1)

    def _read_uma_rank(self, src_region: np.ndarray,
                       uma_loc: Tuple[int, int]) -> int:

        h, w, c = src_region.shape
        start_y = max(uma_loc[1] + 50, 0)
        end_y = min(uma_loc[1] + 75, h)
        start_x = max(uma_loc[0]+22, 0)
        end_x = min(uma_loc[0]+60, w)
        rank_img = src_region[start_y:end_y, start_x:end_x]

        def func(i):
            hr, wr, _ = rank_img.shape
            ht, wt, _ = self.template_rank[i].shape

            if hr < ht or wr < wt:
                return 1  # kuso hikui hyoukati
            method = cv2.TM_SQDIFF_NORMED

            # Apply template Matching
            res = cv2.matchTemplate(rank_img, self.template_rank[i], method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            return min_val

        min_values = [func(i) for i in range(self.rank_num)]
        min_idx = min_values.index(min(min_values))
        rank = min_idx + 1

        # print('min_val:', min_values[min_idx])

        if min_values[min_idx] > 0.07:
            return None

        return rank

    def _make_uma_rank_dict(self):
        src_image = self.snipper.Snip()
        if not src_image:
            return

        rank_rect = (5, 350, 390, 630)
        src_region = pil2cv(src_image.crop(rank_rect))

        def match(template: np.ndarray):
            return cv2.matchTemplate(src_region, template,
                                     cv2.TM_SQDIFF_NORMED)

        match_array = np.stack(
            [match(template) for template in self.template_uma_dict.values()])

        h, w = match_array[0].shape

        match_size = w*h

        max_iter = 10
        uma_name_list = list(self.template_uma_dict.keys())

        def get_uma_loc(min_idx: int, src_size: int) -> Tuple[int, int]:
            flat_idx = min_idx % src_size
            uma_loc_x = flat_idx % w
            uma_loc_y = int(flat_idx/w)
            return (uma_loc_x, uma_loc_y)

        for _ in range(max_iter):
            min_val = np.min(match_array)
            min_idx = match_array.argmin()

            if min_val > 0.04:
                break

            uma_num = int(min_idx/match_size)
            uma_name = uma_name_list[uma_num]

            uma_loc = get_uma_loc(min_idx, match_size)
            # match_array = np.delete(match_array, uma_num, axis=0)
            match_array[uma_num, :] = 1

            uma_rank = self._read_uma_rank(src_region, uma_loc)

            if not uma_rank:
                break

            with self.lock:
                self.uma_rank_dict[uma_name] = uma_rank

    def get(self):
        with self.lock:
            return self.uma_rank_dict.copy()


if __name__ == "__main__":
    rank_reader = RankReadThread()
    rank_reader.start()

    time.sleep(1)
    res = rank_reader.get()
    pprint(res)
    print('num:', len(res))

    rank_reader.stop()
    rank_reader.join()