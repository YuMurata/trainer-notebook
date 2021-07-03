from ctypes import wintypes, pointer, windll
from typing import List, NamedTuple
from PIL import ImageGrab, Image
from tkinter import messagebox
from pathlib import Path
from logger import init_logger
import random
from enum import Enum
from collections import UserList

logger = init_logger(__name__)


class SnipSize(NamedTuple):
    width: int
    height: int


class ImageSnipper:
    snip_size = SnipSize(404, 720)

    def __init__(self, app_name='umamusume'):
        self.app_name = app_name
        self.display_warning = False

    def _GetWindowRectFromName(self) -> tuple:
        TargetWindowHandle = windll.user32.FindWindowW(
            0, self.app_name)
        if TargetWindowHandle == 0:
            return None

        Rectangle = wintypes.RECT()

        windll.user32.GetWindowRect(
            TargetWindowHandle, pointer(Rectangle))
        return (Rectangle.left + 8, Rectangle.top + 30,
                Rectangle.right - 8, Rectangle.bottom - 8)

    def Snip(self) -> Image:
        rect = self._GetWindowRectFromName()

        if rect:
            game_window_image = ImageGrab.grab(rect)

            if not self.display_warning and game_window_image.height < 450:
                messagebox.showwarning('警告', 'ウマ娘の画面が小さいためうまく読み取れない可能性があります')
                self.display_warning = True

            if game_window_image.height == 0:
                return None

            return game_window_image.resize(self.snip_size)

        return None

    @staticmethod
    def get_aspect_ratio() -> float:
        return ImageSnipper.snip_size.width/ImageSnipper.snip_size.height


class BaseDebugSnipper(ImageSnipper):
    def __init__(self, called: str, image_list: List[Image.Image]):
        self.image_list = image_list
        logger.info(f'debug snipper is called from {called}')

    def Snip(self) -> Image.Image:
        image = random.choice(self.image_list)
        return image.resize(self.snip_size)


class RaceScoreSnipper(BaseDebugSnipper):
    def __init__(self, called: str) -> None:
        image_dir = Path('./resource/other/debug/race/score')
        image_list = [Image.open(path)
                      for path in image_dir.iterdir()]
        super().__init__(called, image_list)


class RaceRankSnipper(BaseDebugSnipper):
    def __init__(self, called: str) -> None:
        image_dir = Path('./resource/other/debug/race/rank')
        image_list = [Image.open(path)
                      for path in image_dir.iterdir()]
        super().__init__(called, image_list)


class RaceSnipper(BaseDebugSnipper):
    def __init__(self, called: str) -> None:
        score_dir = Path('./resource/other/debug/race/score')
        score_list = [Image.open(path)
                      for path in score_dir.iterdir()]

        rank_dir = Path('./resource/other/debug/race/rank')
        rank_list = [Image.open(path)
                     for path in rank_dir.iterdir()]
        super().__init__(called, score_list+rank_list)


class DebugSnipperType(Enum):
    RaceScore = RaceScoreSnipper
    RaceRank = RaceRankSnipper
    Race = RaceSnipper
