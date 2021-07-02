import ctypes
from ctypes import wintypes
from typing import NamedTuple
from PIL import ImageGrab, Image
from tkinter import messagebox
from pathlib import Path
from logger import init_logger
import random
from enum import Enum

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
        TargetWindowHandle = ctypes.windll.user32.FindWindowW(
            0, self.app_name)
        if TargetWindowHandle == 0:
            return None

        Rectangle = ctypes.wintypes.RECT()

        ctypes.windll.user32.GetWindowRect(
            TargetWindowHandle, ctypes.pointer(Rectangle))
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
    def __init__(self, called: str, image_dir: Path):
        self.image_list = [Image.open(path)
                           for path in image_dir.iterdir()]
        logger.info(f'debug snipper is called from {called}')

    def Snip(self) -> Image.Image:
        image = random.choice(self.image_list)
        return image.resize(self.snip_size)


class RaceScoreSnipper(BaseDebugSnipper):
    def __init__(self, called: str) -> None:
        image_dir = Path('./resource/other/debug/race/score')
        super().__init__(called, image_dir)


class DebugSnipperType(Enum):
    RaceScore = RaceScoreSnipper
