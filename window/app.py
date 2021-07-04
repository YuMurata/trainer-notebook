import tkinter as tk
from typing import Tuple
from logger import CustomLogger
logger = CustomLogger(__name__)


class BaseApp:
    def __init__(self, window_generator, master_widget: tk.Toplevel,
                 target_size: Tuple) -> None:
        self.window: tk.Toplevel = None
        self.window_generator = window_generator
        self.master_widget = master_widget
        self.window_pos: Tuple = None
        self.target_size = target_size

    def __del__(self):
        self.close_window()

    def close_window(self):
        if self.window:
            self.window.destroy()
            self.window = None

    def _set_geometry(self):
        width, height = self.target_size
        x, y = self.window_pos
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def Activate(self):
        if not self.window:
            self.window = self.window_generator()
            if not self.window_pos:
                master_x = self.master_widget.winfo_rootx()
                master_y = self.master_widget.winfo_rooty()
                width = self.window.winfo_width()
                # logger.debug(f'master_x: {master_x}')
                # logger.debug(f'width: {width}')
                x = master_x - width
                y = master_y

                self.window_pos = x, y
                # logger.debug(f'pos: {self.window_pos}')

            # self._set_geometry()

            def memory_pos(event: tk.Event):
                self.window_pos = (self.window.winfo_rootx()-8,
                                   self.window.winfo_rooty()-31)

            self.window.bind('<Configure>', memory_pos)
            self.window.protocol('WM_DELETE_WINDOW', self.close_window)

        else:
            logger.debug('has window')
            self.window.deiconify()
            self.window.lift()

    def lift(self):
        if self.window:
            self.window.lift()

    def iconify(self):
        if self.window:
            self.window.iconify()

    def deiconify(self):
        if self.window:
            self.deiconify()
