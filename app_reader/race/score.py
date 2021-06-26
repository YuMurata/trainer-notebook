from typing import Dict
from app_reader.base_app_reader import BaseAppReader
import pyocr
import pyocr.builders
from PIL import ImageDraw,  ImageEnhance, Image
from Uma import UmaNameFileReader
from logger import init_logger
import difflib
from misc import get_OCR


logger = init_logger(__name__)


class ScoreReader(BaseAppReader):
    def __init__(self):
        self.score_ocr = ScoreOCR()
        self.score_scene_ocr = ScoreSceneOCR()

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


class ScoreOCR:
    def __init__(self):
        self.tool = get_OCR(logger)
        self.all_uma_name_list = UmaNameFileReader.Read()

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
    def __init__(self):
        self.tool = get_OCR(logger)

    def get_score_scene(self, preproc_image: Image.Image) -> str:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=8)
        res = self.tool.image_to_string(preproc_image,
                                        lang="jpn",
                                        builder=builder)

        if len(res) == 0:
            return None

        return res[0].content.replace(' ', '')