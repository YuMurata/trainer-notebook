from typing import Tuple
from Uma import UmaNameFileReader
from snip import ImageSnipper
from misc import pil2cv
import cv2
from PIL import Image
import time
from pprint import pprint
from pathlib import Path
import numpy as np


class UmaRankReader:
    rank_num = 12

    def __init__(self, all_uma_name_list: list):
        self.all_uma_name_list = all_uma_name_list
        self.uma_rank_dict = dict()

        self.rect_size = 285, 78
        self.step_width = 75
        self.division_upper_left_loc = 348, 14
        self.n_division = 5
        self.divide_img = [None] * self.n_division
        self.template_rank = [cv2.imread(
            f'./resource/rank/rank{i+1:02}.png') for i in range(self.rank_num)]
        self.template_uma_dict = {path.stem: Image.open(path) for path in Path(
            './resource/uma_template').iterdir()}

    def _DivideImg(self, src_img):
        divide_y_start = self.division_upper_left_loc[0]
        divide_y_end = self.division_upper_left_loc[0] + self.rect_size[0]

        divide_x_start_list = [self.division_upper_left_loc[1] +
                               self.step_width * i
                               for i in range(self.n_division)]
        divide_x_end_list = [self.division_upper_left_loc[1] +
                             self.step_width * i + self.rect_size[1]
                             for i in range(self.n_division)]

        self.divide_img = [src_img[divide_y_start:divide_y_end,
                                   divide_x_start_list[i]:divide_x_end_list[i]]
                           for i in range(self.n_division)]
        # cv2.imshow("divide_img", self.divide_img[i])
        # cv2.waitKey(0)

    def _ReadUmaRank(self, src_img: np.array, uma_loc: Tuple, uma_name: str):

        rank_img = src_img[uma_loc[0] + 55:uma_loc[0] +
                           80, uma_loc[1]+37:uma_loc[1]+75]

        def func(i):
            method = cv2.TM_SQDIFF_NORMED

            w, h, c = self.template_rank[i].shape[: 3]

            # Apply template Matching
            res = cv2.matchTemplate(rank_img, self.template_rank[i], method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            return min_val

        min_values = [func(i) for i in range(self.rank_num)]
        min_idx = min_values.index(min(min_values))
        rank = min_idx + 1
        # print("rank="+str(rank))

        if min_values[min_idx] > 0.06:
            # return
            pass

        if uma_name in ['ゴールドシップ', 'テイエムオペラオー']:
            rank_img = src_img[uma_loc[0]:uma_loc[0] +
                               80, uma_loc[1]:uma_loc[1]+75]
            cv2.imshow(uma_name, rank_img)
            cv2.waitKey(0)
        self.uma_rank_dict[uma_name] = rank

    def _FindUmaLoc(self, template: np.array):
        def minloc_from_image(i):
            img = self.divide_img[i]
            method = cv2.TM_SQDIFF_NORMED

            w, h, c = template.shape[: 3]

            # Apply template Matching
            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            return min_val, min_loc

        def minloc_from_list():
            minloc_list = [minloc_from_image(i)
                           for i in range(self.n_division)]
            min_list = [minloc[0] for minloc in minloc_list]
            loc_list = [minloc[1] for minloc in minloc_list]

            min_value = min(min_list)
            min_idx = min_list.index(min_value)
            min_loc = loc_list[min_idx]

            return min_value, min_idx, min_loc

        min_value, min_idx, min_loc = minloc_from_list()

        if min_value > 0.05:
            return None

        uma_loc = (min_loc[1] + self.division_upper_left_loc[0], min_loc[0] +
                   self.division_upper_left_loc[1] + self.step_width * min_idx)
        return uma_loc

    def UmaRankListfromImage(self, src_img):
        img = pil2cv(src_img)
        self._DivideImg(img)
        for uma_name, template in self.template_uma_dict.items():
            # self.uma_rank_dict[uma_name] = 1
            uma_loc = self._FindUmaLoc(pil2cv(template))
            if uma_loc:
                self._ReadUmaRank(img, uma_loc, uma_name)
        return self.uma_rank_dict

    def CreateTemplateImg(self, img):
        template = img.crop((26, 70, 82, 129))
        aspect_ratio = template.width / template.height

        target_width = 69

        target_height = (int)(target_width / aspect_ratio)

        return template.resize((target_width, target_height))


def main():

    snipper = ImageSnipper()

    all_uma_name_list = UmaNameFileReader.Read()  # 全てのウマ娘の名前のリスト

    urr = UmaRankReader(all_uma_name_list)

    print("実行したい番号を入力してください")
    print("1．ウマテンプレート作成")
    print("2．順位読み取り")

    inputNum = int(input('-> '))
    #snip_img = snipper.Snip()
    snip_img = Image.open('./resource/snip_img.png')

    start = time.time()
    if inputNum == 1:
        template = urr.CreateTemplateImg(snip_img)
        cv2.imwrite("./resource/uma_template.png", pil2cv(template))
    elif inputNum == 2:
        uma_rank_dict = urr.UmaRankListfromImage(snip_img)
        pprint(uma_rank_dict)
        print('num:', len(uma_rank_dict))

    elapsed_time = time.time() - start
    print("elapsed_time:{0}", format(elapsed_time) + "[sec]")


if __name__ == "__main__":
    main()
    print("村田はげ")