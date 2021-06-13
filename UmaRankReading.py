from Uma import UmaNameFileReader
from snip import ImageSnipper
from misc import pil2cv, cv2pil
import cv2
from PIL import Image
# import glob

from matplotlib import pyplot as plt
import time


class UmaRankReader:
    def __init__(self, all_uma_name_list: list):
        self.all_uma_name_list = all_uma_name_list
        self.uma_rank_dict = dict()

        self.rect_size = 285, 78
        self.step_width = 75
        self.division_upper_left_loc = 348, 14
        self.n_division = 5
        self.divide_img = [None] * self.n_dividion
        self.template_rank = [None]*12
        for i in range(12):
            self.template_rank[i] = cv2.imread(
                './resource/rank/rank{rank:02}.png'.format(rank=i+1))

    def _DivideImg(self, src_img):

        # print(divide_img)
        for i in range(self.n_division):
            self.divide_img[i] = src_img[self.division_upper_left_loc[0]: self.division_upper_left_loc[0] + self.rect_size[0],
                                         self.division_upper_left_loc[1] + self.step_width * i: self.division_upper_left_loc[1] + self.step_width * i + self.rect_size[1]]
            # cv2.imshow("divide_img", self.divide_img[i])
            # cv2.waitKey(0)

    def _ReadUmaRank(self, src_img, uma_loc, uma_name):

        rank_img = src_img[uma_loc[0] + 55:uma_loc[0] +
                           80, uma_loc[1]+37:uma_loc[1]+75]
        # files = glob.glob("./resource/rank/rank*.png")
        # print(files)
        # if uma_name == 'ハルウララ\n':
        #     cv2.imshow("rank_img", rank_img)
        #     cv2.imwrite("rank_snip_img.png", rank_img)
        #     cv2.waitKey(0)
        # cv2.waitKey(0)
        min_values = [None] * 12
        for i in range(12):
            # cv2.imshow("template_rank", template_rank)
            # cv2.waitKey(0)

            method = eval('cv2.TM_SQDIFF_NORMED')

            w, h, c = self.template_rank[i].shape[: 3]

            # Apply template Matching
            res = cv2.matchTemplate(rank_img, self.template_rank[i], method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            min_values[i] = min_val

            # print(min_val, min_loc)

            # top_left = min_loc

            # bottom_right = (top_left[0] + w, top_left[1] + h)

            # #cv2.rectangle(rank_img, top_left, bottom_right, 255, 2)

            # plt.subplot(121), plt.imshow(res, cmap='gray')
            # plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            # plt.subplot(122), plt.imshow(cv2pil(rank_img))
            # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            # plt.suptitle(method)

            # plt.show()

        min_idx = min_values.index(min(min_values))
        rank = min_idx + 1
        # print("rank="+str(rank))

        self.uma_rank_dict[uma_name] = rank

    def _FindUmaLoc(self, src_img, uma_name):
        file_name = './resource/uma_template/' + \
            uma_name.replace('\n', '') + '.png'
        # print(file_name)

        try:
            template = pil2cv(Image.open(file_name))
        except FileNotFoundError:
            return None

        cv2.imshow("template", template)
        cv2.waitKey(0)

        cv2.imshow("template", template)
        cv2.waitKey(0)

        min_values = [None] * self.n_division
        min_locs = [None] * self.n_division
        for i in range(self.n_division):
            img = self.divide_img[i]
            method = eval('cv2.TM_SQDIFF_NORMED')

            w, h, c = template.shape[: 3]

            # Apply template Matching
            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            min_values[i] = min_val
            min_locs[i] = min_loc

            # print(min_val, min_loc)

            top_left = min_loc

            bottom_right = (top_left[0] + w, top_left[1] + h)

            # cv2.rectangle(img, top_left, bottom_right, 255, 2)

            # plt.subplot(121), plt.imshow(res, cmap='gray')
            # plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            # plt.subplot(122), plt.imshow(cv2pil(img))
            # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            # plt.suptitle(method)

            # plt.show()

        min_idx = min_values.index(min(min_values))
        # print(min_idx)
        if min_values[min_idx] > 0.05:
            return None

        uma_loc = (min_locs[min_idx][1] + self.division_upper_left_loc[0], min_locs[min_idx]
                   [0]+self.division_upper_left_loc[1] + self.step_width * min_idx)
        return uma_loc

    def UmaRankListfromImage(self, src_img):
        img = pil2cv(src_img)
        self._DivideImg(img)
        for uma_name in self.all_uma_name_list:
            # self.uma_rank_dict[uma_name] = 1
            uma_loc = self._FindUmaLoc(img, uma_name)
            if uma_loc is not None:
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
    snip_img = snipper.Snip()
    src_img = cv2.imread("./resource/read_rank_test_img.png")
    # cv2.imshow("snip_img", pil2cv(snip_img))
    # cv2.waitKey(0)
    print(src_img.shape)

    all_uma_name_list = UmaNameFileReader.Read()  # 全てのウマ娘の名前のリスト

    # print(all_uma_name_list)
    urr = UmaRankReader(all_uma_name_list)
    # uma_rank_dict = urr.UmaRankListfromImage(snip_img)
    # print(uma_rank_dict)

    print("実行したい番号を入力してください\n　1．ウマテンプレート作成\n　2．順位読み取り\n")
    inputNum = int(input())
    start = time.time()
    if inputNum == 1:
        print('test')
        template = urr.CreateTemplateImg(snip_img)
        # print(template.size)
        # cv2.imshow("snip_img.png", pil2cv(template))
        cv2.imwrite("./resource/uma_template.png", pil2cv(template))
        # cv2.waitKey(0)
    elif inputNum == 2:
        uma_rank_dict = urr.UmaRankListfromImage(snip_img)
        print(uma_rank_dict)

    elapsed_time = time.time() - start
    print("elapsed_time:{0}", format(elapsed_time) + "[sec]")


if __name__ == "__main__":
    main()
