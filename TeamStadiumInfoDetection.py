import os
import pyocr
import pyocr.builders
import cv2
import ctypes
import numpy as np
from PIL import Image, ImageDraw, ImageGrab, ImageEnhance
from enum import Enum
from UmaPointReading import UmaPointReader
from Uma import UmaNameFileReader, UmaPointFileIO

from exception import FileNotFoundException
from pathlib import Path

from threading import Thread
import time

path=";C:\\Program Files\\Tesseract-OCR"
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

class TeamStadiumInfoDetection(Thread):

    #スコア読み取りモードに移行するために「スコア情報」と書いているかを確認する関数
    # 戻り値 bool
    def __init__(self, uma_pt_list:UmaList):
        super().__init__(daemon=True)
        self.st = State.NONE_ST
        self.game_window_image = None

        self.uma_pt_list = uma_pt_list

        self.uma_list = self.uma_pt_list.getUmaList()#全てのウマ娘の名前のリスト

        self.ocr_tool = self.GetOCRTool()
        self.upr = UmaPointReading(self.ocr_tool)#スコア情報読み取るやつ
        self.upr.setUmaList(self.uma_pt_list.getUmaList())
        self.read_score = {}#スコア情報を読み取った結果

        print(self.read_score)


        self.WindowSetting()

        self.is_updating = True

    def canReadScoreInfo(self):
        #「スコア情報」と書かれている部分を切り出す

        if self.game_window_image is None:
            return False

        img = self.game_window_image.copy()
        print(img.size)
        img = img.convert(mode="L")
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = img.crop((150, 20, 240, 50))
        #白抜き文字だから白黒反転
        img = img.point(lambda x: 255 if x < 200 else 0)
        # cv2.imshow("スコア情報", self.pil2cv(img))
        # cv2.waitKey(0)
        tool = pyocr.get_available_tools()[0]
        res = tool.image_to_string(img,
                                lang="jpn",
                                builder=pyocr.builders.LineBoxBuilder(tesseract_layout=8))
        if len(res) == 0:
            return False
        scoreinfo_str = res[0].content.replace(' ','')
        print(scoreinfo_str)

        return scoreinfo_str == 'スコア情報'

    #順位読み取りモードに移行するために「WIN」または「LOSE」と書いているかを確認する関数
    #テンプレートマッチングを用いた
    #戻り値bool
    def canReadRank(self):
        if self.game_window_image is None:
            return False

        img = self.game_window_image.copy()
        img = self.pil2cv(img)
        #img = img[195:270,125:250]
        img = img[175:250,125:250]
        # cv2.imshow("rank", img)
        def load_image():
            resource_dir = './resource'
            image_name_list = ['win.png', 'lose.png']

            def pred(image_name:str):
                resource_path = Path(resource_dir)/image_name

                if not resource_path.exists():
                    raise FileNotFoundException(f"can't read {str(resource_path)}")
                return cv2.imread(str(resource_path))

            return [pred(image_name) for image_name in image_name_list]


        win_lose_img = load_image()
        method = eval('cv2.TM_SQDIFF_NORMED')
        min = 1.0
        for template in win_lose_img:
            temp_result = cv2.matchTemplate(img,template,method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(temp_result)
            if min > min_val:
                min = min_val

        return min < 0.1

    def pil2cv(self, image):
        ''' PIL型 -> OpenCV型 '''
        new_image = np.array(image, dtype=np.uint8)
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
        return new_image

    def cv2pil(self, image):
        ''' OpenCV型 -> PIL型 '''
        new_image = image.copy()
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        new_image = Image.fromarray(new_image)
        return new_image

    def GetWindowRectFromName(self, TargetWindowTitle:str)-> tuple:
        TargetWindowHandle = ctypes.windll.user32.FindWindowW(0, TargetWindowTitle)
        if TargetWindowHandle == 0:
            return None

        Rectangle = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(TargetWindowHandle, ctypes.pointer(Rectangle))
        return (Rectangle.left + 8, Rectangle.top + 30, Rectangle.right - 8, Rectangle.bottom - 8)

    def GetOCRTool(self):
        #インストールしたTesseract-OCRのパスを環境変数「PATH」へ追記する。
        #OS自体に設定してあれば以下の2行は不要
        # path=';C:\\tesseract-ocr'
        # os.environ['PATH'] = os.environ['PATH'] + path

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise FileNotFoundException("No OCR tool found")

        return tools[0]

    #スコア情報を読み取るための前処理
    def ReadScorePreProc(self, img):

        proc_img = img.convert(mode="L")
        proc_img = ImageEnhance.Contrast(proc_img).enhance(1.5)
        #gray2bin(proc_img, 80)
        test_img = proc_img.point(lambda x: x if x < 80 else 255)
        width, height = test_img.size
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([(0, 0), (90, height)], fill='white')
        draw.rectangle([(width-45, 0), (width, height)], fill='white')
        draw.rectangle([(215, 0), (250, height)], fill='white')
        draw.rectangle([(0, 0), (width, 50)], fill='white')
        draw.rectangle([(0, height - 80), (width, height)], fill='white')

        return test_img

    def CreateEvent(self):
        print(f'score: {self.read_score}')
        print(f'score_type: {type(self.read_score)}')

        if self.canReadScoreInfo() and len(self.read_score) < 15:
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
        read_dict = self.upr.UmaPtListfromImage(img)

        for uma_name, point in read_dict.items():
            self.read_score[uma_name] = point

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

    def UpdateImage(self):
        rect = self.GetWindowRectFromName('umamusume')

        if rect is not None:
            self.game_window_image = ImageGrab.grab(rect)
            print(self.game_window_image.size)
            self.game_window_image = self.game_window_image.resize((388,720))
            # cv2.imshow("img", self.pil2cv(self.game_window_image))
            # cv2.waitKey(0)

    def OverWriteUmaListFile(self):
        self.uma_pt_list.addUmaPt(self.read_score)
        self.uma_pt_list.WriteUmaList()

    def stop(self):
        self.is_updating = False

    def run(self):
        while self.is_updating:
            self.UpdateImage()
            self.TransitionST()

            time.sleep(0.5)
