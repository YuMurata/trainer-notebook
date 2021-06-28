from typing import Callable
from PIL import Image
import tkinter as tk
from tkinter import ttk
from logger import init_logger
from .image import ImageStruct

logger = init_logger(__name__)


class StatusFrame(ttk.Frame):
    def __init__(self, master: tk.Widget,
                 add_compare_image: Callable[[ImageStruct], None]):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=400, height=300)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.image_struct: ImageStruct = None
        self.image_id: int = None

        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.config(command=self.canvas.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.scroll.set)
        self.canvas.bind("<MouseWheel>", self._scroll_y)
        self.canvas.bind('<Control-MouseWheel>', self._zoom)
        self.canvas.bind(
            '<Button-1>', lambda _: add_compare_image(self.image_struct))
        self.canvas.bind(
            '<Button-3>', self._delete_image)
        self.scale = 1.0

    def _delete_image(self, event):
        logger.debug('call delete status')
        if not self.image_id:
            return

        self.canvas.delete(self.image_id)
        self.image_id = None
        self.image_struct = None

        self._reconfig_scroll()

        logger.debug('delete status')

    def select_image(self, image: Image.Image):
        self.image_struct = ImageStruct(image)
        self.image_struct.scale(self.scale)
        if not self.image_id:
            self.image_id = self.canvas.create_image(
                0, 0, anchor='nw', image=self.image_struct.photoimage)
        else:
            self.canvas.itemconfig(
                self.image_id, image=self.image_struct.photoimage)

        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲

    def _scroll_y(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

    def change_image(self,
                     image_struct: ImageStruct) -> ImageStruct:
        if not self.image_id or not self.image_struct:
            return None

        scale = self.image_struct.scale_ratio
        change_image = self.image_struct
        self.image_struct = image_struct
        self.image_struct.scale(scale)

        if not self.image_id:
            self.canvas.create_image(
                0, 0, anchor='nw', image=self.image_struct.photoimage)
        else:
            self.canvas.itemconfig(
                self.image_id, image=self.image_struct.photoimage)

        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲

        return change_image

    def _zoom(self, event: tk.Event):
        step = 0.25 if event.delta > 0 else -0.25

        self.image_struct.step_scale(step)
        self.canvas.itemconfig(
            self.image_id, image=self.image_struct.photoimage)
        self.scale = self.image_struct.scale_ratio

        self._reconfig_scroll()

    def _reconfig_scroll(self):
        self.canvas.update_idletasks()
        scrollregion = self.canvas.bbox("all")
        if not scrollregion:
            scrollregion = (0, 0, 0, 0)
        self.canvas.config(scrollregion=scrollregion)  # スクロール範囲

    def clear(self, event):
        self._delete_image(event)
