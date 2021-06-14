import os
import pyocr
import pyocr.builders
import cv2
from PIL import ImageDraw,  ImageEnhance
from enum import Enum
from UmaPointReading import UmaPointReader
from Uma import UmaNameFileReader, UmaPointFileIO
from exception import FileNotFoundException
from pathlib import Path
from threading import Thread
import time
from snip import ImageSnipper
from misc import pil2cv

path = ";C:\\Program Files\\Tesseract-OCR"
os.environ['PATH'] = os.environ['PATH'] + path
print(os.environ['PATH'])


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


class TeamStadiumInfoDetection(Thread):

    # スコア読み取りモードに移行するために「スコア情報」と書いているかを確認する関数
    # 戻り値 bool
    def __init__(self, score_dispatcher: ScoreDispatcher):
        super().__init__()
        self.st = State.NONE_ST
        self.snipper = ImageSnipper()
        self.game_window_image = self.snipper.Snip()
        self.all_uma_name_list = UmaNameFileReader.Read()  # 全てのウマ娘の名前のリスト
        self.uma_info_dict = UmaPointFileIO.Read()
        self.ocr_tool = self.GetOCRTool()
        self.upr = UmaPointReader(
            self.ocr_tool, self.all_uma_name_list)  # スコア情報読み取るやつ
        self.score_dispatcher = score_dispatcher  # スコア情報を読み取った結果

        self.display_warning = False  # 画面が小さいことを警告したかどうか

        # EV_mat = [[None, ]]#状態遷移を2次元配列で作ろうとしたけどあきらめた

        self.is_updating = True

    def canReadScoreInfo(self):
        # 「スコア情報」と書かれている部分を切り出す

        if self.game_window_image is None:
            return False

        img = self.game_window_image.copy()
        print(img.size)

        img = img.convert(mode="L")
        img = ImageEnhance.Contrast(img).enhance(1.5)

        img = img.crop((150, 20, 255, 50))

        # 白抜き文字だから白黒反転
        img = img.point(lambda x: 255 if x < 200 else 0)

        # cv2.imshow("score", self.pil2cv(img))
        # cv2.waitKey(0)

        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=8)
        res = self.ocr_tool.image_to_string(img,
                                            lang="jpn",
                                            builder=builder)

        if len(res) == 0:
            return False

        scoreinfo_str = res[0].content.replace(' ', '')
        print(scoreinfo_str)

        return scoreinfo_str == 'スコア情報'

    # 順位読み取りモードに移行するために「WIN」または「LOSE」と書いているかを確認する関数
    # テンプレートマッチングを用いた
    # 戻り値bool
    def canReadRank(self):
        if self.game_window_image is None:
            return False

        img = self.game_window_image.copy()
        img = pil2cv(img)

        img = img[175:250, 130:265]

        # cv2.imshow("rank", self.pil2cv(img))
        # cv2.waitKey(0)

        def load_image():
            resource_dir = './resource'
            image_name_list = ['win.png', 'lose.png']

            def pred(image_name: str):
                resource_path = Path(resource_dir)/image_name

                if not resource_path.exists():
                    raise FileNotFoundException(
                        f"can't read {str(resource_path)}")
                return cv2.imread(str(resource_path))

            return [pred(image_name) for image_name in image_name_list]

        win_lose_img = load_image()
        method = eval('cv2.TM_SQDIFF_NORMED')
        min = 1.0
        for template in win_lose_img:
            temp_result = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(temp_result)
            if min > min_val:
                min = min_val

        return min < 0.1

    def GetOCRTool(self):
        # インストールしたTesseract-OCRのパスを環境変数「PATH」へ追記する。
        # OS自体に設定してあれば以下の2行は不要
        # path=';C:\\tesseract-ocr'
        # os.environ['PATH'] = os.environ['PATH'] + path

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise FileNotFoundException("No OCR tool found")

        return tools[0]

    # スコア情報を読み取るための前処理
    def ReadScorePreProc(self, img):

        proc_img = img.convert(mode="L")
        proc_img = ImageEnhance.Contrast(proc_img).enhance(1.5)
        test_img = proc_img.point(lambda x: x if x < 80 else 255)
        width, height = test_img.size
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([(0, 0), (90, height)], fill='white')
        draw.rectangle([(width-48, 0), (width, height)], fill='white')
        draw.rectangle([(230, 0), (260, height)], fill='white')
        draw.rectangle([(0, 0), (width, 50)], fill='white')
        draw.rectangle([(0, height - 80), (width, height)], fill='white')

        # cv2.imshow("preproc", self.pil2cv(test_img))
        # cv2.waitKey(0)

        return test_img

    def CreateEvent(self):
        read_score = self.score_dispatcher.current_score
        if self.canReadScoreInfo() and len(read_score) < 15:
            return Event.READ_SCORE_START_EV

        elif self.canReadRank():
            return Event.READ_RANK_START_EV
        else:
            return Event.NONE_EV

    def onNoneST(self, ev):
        if ev == Event.NONE_EV:
            pass
        elif ev == Event.READ_SCORE_START_EV:
            self.st = State.READ_SCORE_ST

        elif ev == Event.READ_SCORE_END_EV:
            pass

        elif ev == Event.READ_RANK_START_EV:
            self.st = State.READ_RANK_ST
            pass

        elif ev == Event.READ_RANK_END_EV:
            pass

    def onReadScoreST(self, ev):

        img = self.ReadScorePreProc(self.game_window_image)
        read_score = self.upr.UmaPtListfromImage(img)
        print(f'from image: {read_score}')
        self.score_dispatcher.update_score(read_score)

        if ev == Event.NONE_EV:
            pass
        elif ev == Event.READ_SCORE_START_EV:
            pass
        elif ev == Event.READ_SCORE_END_EV:
            self.st = State.NONE_ST
        elif ev == Event.READ_RANK_START_EV:
            self.st = State.READ_RANK_ST
        elif ev == Event.READ_RANK_END_EV:
            self.st = State.NONE_ST

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
        print('st:'+str(self.st)+'：ev:'+str(ev))
        if self.st == State.NONE_ST:
            self.onNoneST(ev)

        elif self.st == State.READ_SCORE_ST:
            self.onReadScoreST(ev)

        elif self.st == State.READ_RANK_ST:
            self.onReadRankST(ev)

    def OverWriteUmaListFile(self):
        for name, point in self.read_score.items():
            self.uma_info_dict[name].AddPoint(point)

        UmaPointFileIO.Write(self.uma_info_dict)

    def stop(self):
        self.is_updating = False

    def run(self):
        while self.is_updating:
            self.game_window_image = self.snipper.Snip()
            if self.game_window_image:
                self.TransitionST()

            time.sleep(0.5)
