from typing import Dict, List, Tuple
from snip import ImageSnipper
from misc import concat_imshow, pil2cv
import cv2
from PIL import Image
import numpy as np
from TeamStadiumInfoDetection.linked_reader import LinkedReader
from .define import template_dir
from logger import init_logger
logger = init_logger(__name__)


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


class RankReader(LinkedReader):
    rank_num = 12

    def __init__(self):
        self.snipper = ImageSnipper()

        rank_template_dir = template_dir/'rank'
        self.template_rank = [cv2.imread(
            str(rank_template_dir/f'rank{i+1:02}.png'))
            for i in range(self.rank_num)]

        uma_template_dir = template_dir/'uma'
        self.template_uma_dict = {
            path.stem: pil2cv(Image.open(path))
            for path in uma_template_dir.iterdir()}

        self.is_update = True

    def can_read(self, snip_image: Image.Image):
        img = pil2cv(snip_image)

        img = img[175:250, 130:265]

        def load_image() -> List[np.ndarray]:
            result_template_dir = template_dir/'race_result'
            return [cv2.imread(str(path))
                    for path in result_template_dir.iterdir()]

        win_lose_img = load_image()
        method = cv2.TM_SQDIFF_NORMED

        def match(template: np.ndarray):
            temp_result = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(temp_result)
            return min_val

        min_val = min([match(template) for template in win_lose_img])
        # if(min_val < 0.05):
        #     print("minval", min_val)
        #     cv2.imshow("test", img)
        #     cv2.waitKey(0)

        return min_val < 0.05

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

    def read(self, snip_image: Image.Image) -> Dict[str, int]:
        rank_rect = (5, 350, 390, 630)
        src_region = pil2cv(snip_image.crop(rank_rect))

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

        uma_rank_dict = dict()

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

            uma_rank_dict[uma_name] = uma_rank

        return uma_rank_dict
