import ctypes
from PIL import ImageGrab
from tkinter import Image, messagebox


class ImageSnipper:
    def __init__(self, app_name='umamusume'):
        self.app_name = app_name
        self.display_warning = False
        pass

    def _GetWindowRectFromName(self, TargetWindowTitle: str) -> tuple:
        TargetWindowHandle = ctypes.windll.user32.FindWindowW(
            0, TargetWindowTitle)
        if TargetWindowHandle == 0:
            return None

        Rectangle = ctypes.wintypes.RECT()

        ctypes.windll.user32.GetWindowRect(
            TargetWindowHandle, ctypes.pointer(Rectangle))
        return (Rectangle.left + 8, Rectangle.top + 30,
                Rectangle.right - 8, Rectangle.bottom - 8)

    def Snip(self) -> Image:
        rect = self._GetWindowRectFromName(self.app_name)

        if rect:
            game_window_image = ImageGrab.grab(rect)

            if not self.display_warning and game_window_image.height < 450:
                messagebox.showwarning('警告', 'ウマ娘の画面が小さいためうまく読み取れない可能性があります')
                self.display_warning = True

            aspect_ratio = game_window_image.width / game_window_image.height

            target_height = 720

            target_width = (int)(target_height * aspect_ratio)
            return game_window_image.resize((target_width, target_height))

        return None
