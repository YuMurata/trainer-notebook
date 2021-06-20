from typing import Dict, List, Tuple
from misc import StopWatch, cv2pil, pil2cv
from snip import ImageSnipper
from PIL import Image
import cv2
import numpy as np
from misc import concat_imshow
from similarity import ccoeff_normed
import os
import pyocr
from exception import FileNotFoundException
from difflib import SequenceMatcher
from pathlib import Path


class debugger:
    @staticmethod
    def show_rect(src_reagion: np.ndarray,
                  rect_dict: Dict[str, Tuple[Tuple[int, int],
                                             Tuple[int, int]]]):
        copy_reagion = src_reagion.copy()

        color_list = [(0, 0, 0), (255, 0, 0), (0, 0, 255),
                      (0, 205, 205), (150, 150, 255), (0, 255, 0)]
        color_dict = {key: color for key, color in zip(
            rect_dict.keys(), color_list)}

        for key, rect in rect_dict.items():
            cv2.rectangle(copy_reagion, rect[0], rect[1], color_dict[key], 3)

        cv2.imshow('rect', src_reagion)
        cv2.waitKey(0)

    @staticmethod
    def show_region(region_dict: Dict[str, np.ndarray]):
        concat_imshow('region', list(region_dict.values()))
        cv2.waitKey(0)


class TrainingReader:
    def __init__(self, tool):
        self.snipper = ImageSnipper()
        self.tool = tool

    def can_read(self, snip_image: Image.Image) -> bool:
        region_left_top = (10, 525)
        region_right_bottom = (395, 670)
        src_region = pil2cv(snip_image)[
            region_left_top[1]:region_right_bottom[1],
            region_left_top[0]:region_right_bottom[0]]

        template = cv2.imread('./resource/template/training.png')
        # gray_template = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
        # gray_src = cv2.cvtColor(src_region, cv2.COLOR_RGB2GRAY)

        threshold = 0.4
        return ccoeff_normed(src_region, template) > threshold

    def _read_status(self, region: Image.Image) -> List[int]:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=6)
        builder.tesseract_configs.append("digits")
        res = self.tool.image_to_string(region, lang="eng", builder=builder)
        read_list = [d.content.replace(' ', '') for d in res]
        status_list = [int(read) for read in read_list if read.isdecimal()]
        status_num = 5
        return status_list if len(status_list) == status_num else None

    def _read_season(self, region: Image.Image) -> str:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=6)
        tesseract_config = str(Path('./season').absolute())
        builder.tesseract_configs.extend([tesseract_config])
        res = self.tool.image_to_string(region, lang="jpn", builder=builder)
        read = [d.content.replace(' ', '') for d in res][0]

        grade_list = ['ジュニア級', 'クラシック級', 'シニア級', 'ファイナルズ']
        season_list = [f'{month}月{half}半' for month in range(1, 12)
                       for half in ['前', '後']]
        season_list.extend(['デビュー前', '開催中'])

        def ratio(target: str, part_read: str) -> float:
            return SequenceMatcher(None, target, part_read).ratio()
        grade_tuple = max([(grade, ratio(grade, read[:len(grade)]))
                           for grade in grade_list], key=lambda x: x[1])
        season_tuple = max([(season, ratio(season, read[-len(season):]))
                            for season in season_list], key=lambda x: x[1])

        threshold = 0.5
        grade = grade_tuple[0] if grade_tuple[1] > threshold else '?'
        season = season_tuple[0] if season_tuple[1] > threshold else '?'
        return f'{grade} {season}'

    def read(self, snip_image: Image.Image) -> Dict[str, Dict[str, int]]:
        src_reagion = pil2cv(snip_image)
        # status_wh=(40, 15)
        rect_dict = {'season': ((5, 20), (125, 40)),
                     'speed': ((35, 480), (75, 495)),
                     'stamina': ((105, 480), (140, 495)),
                     'power': ((166, 480), (202, 495)),
                     'guts': ((230, 480), (265, 495)),
                     'intel': ((295, 480), (330, 495))}

        region_dict = {key: src_reagion[rect[0][1]:rect[1][1],
                                        rect[0][0]:rect[1][0]]
                       for key, rect in rect_dict.items()}

        status_key_list = [key for key in rect_dict.keys() if key != 'season']
        max_status_w = max([rect_dict[key][1][0]-rect_dict[key][0][0]
                           for key in status_key_list])

        def border(image: np.ndarray) -> np.ndarray:
            w = image.shape[1]
            return cv2.copyMakeBorder(image, 0, 0,  max_status_w-w, 0,
                                      cv2.BORDER_CONSTANT,
                                      value=(255, 255, 255))
        concat_status_image = cv2.vconcat(
            [border(region_dict[key]) for key in status_key_list])

        with StopWatch('season'):
            season = self._read_season(cv2pil(region_dict['season']))

        with StopWatch('status'):
            status_list = self._read_status(cv2pil(concat_status_image))

        if not status_list:
            return None

        return {key: val for key, val in zip(['season']+status_key_list,
                                             [season]+status_list)}


def _get_OCR_tool():
    # インストールしたTesseract-OCRのパスを環境変数「PATH」へ追記する。
    # OS自体に設定してあれば以下の2行は不要
    path = ';C:\\tesseract-ocr'
    path = ";C:\\Program Files\\Tesseract-OCR"
    os.environ['PATH'] = os.environ['PATH'] + path

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        raise FileNotFoundException("No OCR tool found")

    return tools[0]


if __name__ == '__main__':
    shot_id = '20210619-020323'
    snip_image = Image.open(
        f'./resource/screenshot/{shot_id}.png').resize((404, 720))
    print(TrainingReader(_get_OCR_tool()).read(snip_image))
