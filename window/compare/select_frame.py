from typing import Callable,  Dict
from snip import ImageSnipper
from PIL import Image
import tkinter as tk
from tkinter import ttk
from logger import CustomLogger
from .umaframe import UmaFrame, ButtonFunc

logger = CustomLogger(__name__)


class SelectFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, snipper: ImageSnipper,
                 show_image_status: Callable[[Image.Image], None],
                 show_image_compare: Callable[[Image.Image], None]):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=400, bg='white')
        self.snipper = snipper
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.config(command=self.canvas.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.scroll.set)
        self.set_mousewheel(self.canvas, self._scroll_y)

        self.umaframe_dict: Dict[int, UmaFrame] = dict()
        self.show_image_status = show_image_status
        self.show_image_compare = show_image_compare
        self.add_umaframe()

    def set_mousewheel(self, widget, command):
        """Active / deactivate mousewheel scrolling when
        cursor is over / not over the widget respectively."""
        widget.bind("<Enter>", lambda e: widget.bind_all(
            '<MouseWheel>', lambda e: command(e)))
        widget.bind("<Leave>", lambda e: widget.unbind_all('<MouseWheel>'))

    def _get_frame_y_end(self):
        y_end = 0
        bbox = self.canvas.bbox("all")
        if bbox:
            y_end = bbox[3] + 10

        return y_end

    def _get_frame_xy(self, frame_idx: int):
        x = 0
        height = 0

        for i, umaframe in enumerate(self.umaframe_dict.values()):
            if i == frame_idx:
                break
            height += umaframe.winfo_height()
        y = height
        return x, y

    def add_umaframe(self):
        button_func = ButtonFunc(
            self.show_image_status, self.show_image_compare, self.add_umaframe,
            self.delete_umaframe)
        umaframe = UmaFrame(self.canvas, self.snipper,
                            button_func)

        item_id = self.canvas.create_window(
            self._get_frame_xy(len(self.umaframe_dict)), window=umaframe,
            anchor='nw', width=self.canvas.cget("width"))
        umaframe.set_item_id(item_id)

        self._reconfig_scroll()
        self.umaframe_dict[item_id] = umaframe

    def _reconfig_scroll(self):
        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲

    def delete_umaframe(self, delete_id: int):
        if len(self.umaframe_dict) <= 1:
            return
        if not self.umaframe_dict[delete_id].image:
            return

        self.umaframe_dict.pop(delete_id)
        self.canvas.delete(delete_id)

        for i, item_id in enumerate(self.umaframe_dict.keys()):
            self.canvas.moveto(item_id, *self._get_frame_xy(i))

        self._reconfig_scroll()

    def all_delete_umaframe(self, event):
        item_list = list(self.umaframe_dict.items())
        for item_id, umaframe in item_list:
            if len(self.umaframe_dict) == 1:
                break

            if umaframe.image:
                self.umaframe_dict.pop(item_id)
                self.canvas.delete(item_id)

        for i, item_id in enumerate(self.umaframe_dict.keys()):
            self.canvas.moveto(item_id, *self._get_frame_xy(i))

        self._reconfig_scroll()

    def _scroll_y(self, event):
        if self._get_frame_y_end() < self.canvas.winfo_height():
            return
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')
