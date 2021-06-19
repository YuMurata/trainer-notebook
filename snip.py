from ctypes import wintypes, pointer, windll
from PIL import ImageGrab
from tkinter import Image, messagebox


class ImageSnipper:
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

            aspect_ratio = game_window_image.width / game_window_image.height

            target_height = 720

            target_width = (int)(target_height * aspect_ratio)
            return game_window_image.resize((target_width, target_height))

        return None
