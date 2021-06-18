from typing import Tuple, Dict
from TeamStadiumInfoDetection.dispatcher import BaseDispatched, Dispatcher
from TeamStadiumInfoDetection.linked_reader import LinkedReader
import os
import pyocr
import pyocr.builders
import cv2
from PIL import ImageDraw,  ImageEnhance, Image
from enum import Enum
from UmaPointReading import UmaPointReader
from Uma import UmaNameFileReader, UmaPointFileIO
from exception import FileNotFoundException, InvalidTypeException
from pathlib import Path
from threading import Thread, RLock
import time
from snip import ImageSnipper
from misc import pil2cv
from logger import init_logger
import difflib


logger = init_logger(__name__)

path = ";C:\\Program Files\\Tesseract-OCR"
os.environ['PATH'] = os.environ['PATH'] + path
logger.debug(os.environ['PATH'])


class State(Enum):
    NONE_ST = 0
    READ_SCORE_ST = 1
    READ_RANK_ST = 2


class Event(Enum):
    NONE_EV = 0
    READ_SCORE_START_EV = 1
    READ_SCORE_END_EV = 2
    READ_RANK_START_EV = 3
    READ_RANK_END_EV = 4


class ScoreDispatcher:
    def __init__(self, callback):
        self.init_score()
        self.callback = callback

    def update_score(self, score: dict):
        self.current_score.update(score)
        if self.current_score != self.old_score:
            self.callback(self.current_score)

        self.old_score = {key: value for key,
                          value in self.current_score.items()}

    def init_score(self):
        self.current_score = dict()
        self.old_score = dict()


class ScoreDispatched(BaseDispatched):
    def __init__(self, score_dict: dict) -> None:
        super().__init__()
        self.score_dict = score_dict.copy()

    def init_item(self):
        self.score_dict = dict()

    def update_current(self, item: object):
        if type(item) != type(self):
            raise InvalidTypeException(f'except {str(type(self))}')

        self.score_dict.update(item.score_dict)

    def update_old(self, current_item: object):
        self.score_dict = current_item.score_dict.copy()

    def __ne__(self, item: object) -> bool:
        if type(item) != type(self):
            return False
        return self.score_dict != item.score_dict

    def copy(self):
        return ScoreDispatched(self.score_dict)


def _get_OCR():
    # インストールしたTesseract-OCRのパスを環境変数「PATH」へ追記する。
    # OS自体に設定してあれば以下の2行は不要
    # path=';C:\\tesseract-ocr'
    # os.environ['PATH'] = os.environ['PATH'] + path

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        raise FileNotFoundException("No OCR tool found")

    return tools[0]


class ScoreReader(LinkedReader):
    def __init__(self):
        tool = _get_OCR()
        self.score_ocr = ScoreOCR(tool)
        self.score_scene_ocr = ScoreSceneOCR(tool)

    # 順位読み取りモードに移行するために「WIN」または「LOSE」と書いているかを確認する関数
    # テンプレートマッチングを用いた
    def can_read(self, snip_image: Image.Image):
        # 「スコア情報」と書かれている部分を切り出す

        img = snip_image.convert(mode="L")
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = img.crop((150, 20, 255, 50))

        # 白抜き文字だから白黒反転
        img = img.point(lambda x: 255 if x < 200 else 0)

        score_scene_str = self.score_scene_ocr.get_score_scene(img)
        if not score_scene_str:
            return False

        return score_scene_str == 'スコア情報'

    # スコア情報を読み取るための前処理

    def _pre_proc(self, snip_image: Image.Image):

        proc_img = snip_image.convert(mode="L")
        proc_img = ImageEnhance.Contrast(proc_img).enhance(1.5)
        test_img = proc_img.point(lambda x: x if x < 80 else 255)
        width, height = test_img.size
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([(0, 0), (90, height)], fill='white')
        draw.rectangle([(width-48, 0), (width, height)], fill='white')
        draw.rectangle([(230, 0), (260, height)], fill='white')
        draw.rectangle([(0, 0), (width, 50)], fill='white')
        draw.rectangle([(0, height - 80), (width, height)], fill='white')

        return test_img

    def read(self, snip_image: Image.Image):

        preproc_image = self._pre_proc(snip_image)
        return self.score_ocr.get_score(preproc_image)

    def onReadRankST(self, ev):
        if ev == Event.NONE_EV:
            pass
        elif ev == Event.READ_SCORE_START_EV:
            self.st = State.READ_SCORE_ST
        elif ev == Event.READ_SCORE_END_EV:
            self.st = State.NONE_ST
        elif ev == Event.READ_RANK_START_EV:
            pass
        elif ev == Event.READ_RANK_END_EV:
            self.st = State.NONE_ST

    def TransitionST(self):
        ev = self.CreateEvent()
        # print('st:'+str(self.st)+'：ev:'+str(ev))
        if self.st == State.NONE_ST:
            self.onNoneST(ev)

        elif self.st == State.READ_SCORE_ST:
            self.onReadScoreST(ev)

        elif self.st == State.READ_RANK_ST:
            self.onReadRankST(ev)

    def OverWriteUmaListFile(self):
        uma_info_dict = UmaPointFileIO.Read()

        with self.lock:
            for name, point in self.score_dict.items():
                uma_info_dict[name].AddPoint(point)

        UmaPointFileIO.Write(uma_info_dict)

    def stop(self):
        self.is_updating = False

    def run(self):
        while self.is_updating:
            self.game_window_image = self.snipper.Snip()
            if self.game_window_image:
                self.TransitionST()

            logger.debug('get lock')
            with self.lock:
                self.dispatcher.update_item(
                    ScoreDispatched(self.score_dict.copy()))
            logger.debug('release lock')

            time.sleep(0.5)

    def get(self):
        logger.debug('get lock')
        with self.lock:
            logger.debug('copy score')
            score_dict = self.score_dict.copy()
        logger.debug('return')
        return score_dict


class ScoreOCR:
    def __init__(self, tool):
        self.tool = tool
        self.all_uma_name_list = UmaNameFileReader.Read()

    def _get_OCR(self):
        # インストールしたTesseract-OCRのパスを環境変数「PATH」へ追記する。
        # OS自体に設定してあれば以下の2行は不要
        # path=';C:\\tesseract-ocr'
        # os.environ['PATH'] = os.environ['PATH'] + path

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise FileNotFoundException("No OCR tool found")

        return tools[0]

    def _extract_score(self, line: str) -> int:
        for word in line.split(' '):
            if 'pt' in word:
                if word.split('pt')[0].isdecimal():
                    return int(word.split('pt')[0])
                else:
                    return None
        return None

    def _extract_name(self, line: str, score: int) -> str:
        extract_name = line.replace(' ', '').split(str(score))[0]

        def match(uma_name: str):
            return difflib.SequenceMatcher(None, uma_name,
                                           extract_name).ratio()

        match_list = [(uma_name, match(uma_name))
                      for uma_name in self.all_uma_name_list]

        uma_name, max_match = max(match_list, key=lambda x: x[1])

        if max_match < 0.6:
            return None

        return uma_name

    def get_score(self, preproc_image: Image.Image) -> Dict[str, int]:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=6)
        res = self.tool.image_to_string(
            preproc_image, lang="jpn", builder=builder)

        def rm_point(line: str):
            return line.replace(',', '').replace('.', '').replace('、', '')

        line_list = [rm_point(d.content) for d in res]
        score_list = [self._extract_score(line) for line in line_list]
        score_dict = {self._extract_name(line, score): score
                      for score, line in zip(score_list, line_list) if score}

        return score_dict


class ScoreSceneOCR:
    def __init__(self, tool):
        self.tool = tool

    def get_score_scene(self, preproc_image: Image.Image) -> str:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=8)
        res = self.tool.image_to_string(preproc_image,
                                        lang="jpn",
                                        builder=builder)

        if len(res) == 0:
            return None

        return res[0].content.replace(' ', '')
