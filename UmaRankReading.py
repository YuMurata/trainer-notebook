from threading import Thread, Lock
from typing import Tuple
from Uma import UmaNameFileReader
from snip import ImageSnipper
from misc import concat_imshow, pil2cv, MouseXYGetter
import cv2
from PIL import Image
import time
from pprint import pprint
from pathlib import Path
import numpy as np


class UmaRankReadThread(Thread):
    rank_num = 12

    def __init__(self):
        super().__init__()
        self.snipper = ImageSnipper()
        self.all_uma_name_list = UmaNameFileReader().Read()
        self.lock = Lock()
        self.uma_rank_dict = dict()

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
            method = cv2.TM_SQDIFF_NORMED

            # Apply template Matching
            res = cv2.matchTemplate(rank_img, self.template_rank[i], method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            return min_val

        min_values = [func(i) for i in range(self.rank_num)]
        min_idx = min_values.index(min(min_values))
        rank = min_idx + 1

        return rank

    def _make_uma_rank_dict(self):
        src_image = self.snipper.Snip()
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

            with self.lock:
                self.uma_rank_dict[uma_name] = uma_rank

    def get(self):
        with self.lock:
            return self.uma_rank_dict.copy()


def main():

    snipper = ImageSnipper()

    all_uma_name_list = UmaNameFileReader.Read()  # 全てのウマ娘の名前のリスト

    urr = UmaRankReader(all_uma_name_list)

    print("実行したい番号を入力してください")
    print("1．ウマテンプレート作成")
    print("2．順位読み取り")
    print("3．矩形サイズ表示")

    #inputNum = int(input('-> '))
    inputNum = 2
    snip_img = snipper.Snip()

    snip_img = Image.open('./resource/snip_img.png')

    start = time.time()
    if inputNum == 1:

        uma_name = None
        while uma_name not in all_uma_name_list:
            uma_name = input("作成するウマ娘の名前を入力してください\n->") + '\n'
        # uma_name = 'test'
        template = urr.CreateTemplateImg(snip_img)
        uma_name = uma_name.replace('\n', '')
        template.save(f"./resource/uma_template/{uma_name}.png")
        # cv2.imshow(uma_name, pil2cv(template))
        # cv2.waitKey(0)

    elif inputNum == 2:
        uma_rank_dict = urr.UmaRankListfromImage(snip_img)
        pprint(uma_rank_dict)
        print('num:', len(uma_rank_dict))

    elif inputNum == 3:
        MouseXYGetter().get(pil2cv(snip_img))

    elapsed_time = time.time() - start
    print("elapsed_time:{0}", format(elapsed_time) + "[sec]")


if __name__ == "__main__":
    main()
