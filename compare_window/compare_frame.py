from sys import setcheckinterval
from exception import IllegalInitializeException
from typing import Callable, Dict, List, NamedTuple
from PIL import ImageTk
import tkinter as tk
from tkinter import ttk
from logger import init_logger
from .image import ImageStruct, ImageStructDict

logger = init_logger(__name__)


class StatusFunc(NamedTuple):
    change: Callable[[ImageStruct], ImageStruct]


class CompareFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, expand=True, side=tk.LEFT)

        self.canvas = tk.Canvas(frame, bg='blue', height=300)
        self.canvas.pack(fill=tk.X, expand=True)

        self.x_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        self.x_scroll.config(command=self.canvas.xview)
        self.x_scroll.pack(fill=tk.X, expand=True)

        self.y_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.y_scroll.config(command=self.canvas.yview)
        self.y_scroll.pack(fill=tk.Y, expand=True, anchor=tk.E)

        self.canvas.config(xscrollcommand=self.x_scroll.set,
                           yscrollcommand=self.y_scroll.set)

        self.canvas.bind("<MouseWheel>", self._scroll_y)
        self.canvas.bind("<Shift-MouseWheel>", self._scroll_x)
        self.canvas.bind('<Control-MouseWheel>', self._zoom)

        self.canvas.tag_bind('status', '<Button-1>', self._change_image)
        self.canvas.tag_bind('status', '<Button-3>', self._delete_image)

        self.image_dict = ImageStructDict()
        self.status_func: StatusFunc = None

    def _zoom(self, event: tk.Event):
        step = 0.25 if event.delta > 0 else -0.25

        self.image_dict.step_scale(step)

        old_item_id = None
        for item_id in self.image_dict.keys():
            photoimage = self.image_dict[item_id].photoimage
            self.canvas.itemconfig(item_id, image=photoimage)
            self.canvas.moveto(item_id, *self._get_image_xy(old_item_id))
            old_item_id = item_id

        self._reconfig_scroll()

    def set_status_func(self, status_func: StatusFunc):
        self.status_func = status_func

    def _change_image(self, event: tk.Event):
        if not self.status_func:
            raise IllegalInitializeException('status_func is not initialized')

        item_id_list: List[int] = self.canvas.find_closest(event.x, event.y)

        if len(item_id_list) < 1:
            return

        item_id = item_id_list[0]
        # print(item_id_list)

        if item_id not in self.image_dict:
            return

        scale = self.image_dict.scale_ratio
        image_struct = self.status_func.change(
            self.image_dict[item_id])
        image_struct.scale(scale)

        if not image_struct:
            return

        self.canvas.itemconfig(item_id, image=image_struct.photoimage)
        self.image_dict[item_id] = image_struct

        self._reconfig_scroll()

    def _delete_image(self, event: tk.Event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        item_id_list: List[int] = self.canvas.find_closest(x, y)

        if len(item_id_list) < 1:
            return

        item_id = item_id_list[0]

        if item_id not in self.image_dict:
            return

        self.image_dict.pop(item_id)
        self.canvas.delete(item_id)

        old_item_id = None
        for i, item_id in enumerate(self.image_dict.keys()):
            self.canvas.moveto(item_id, *self._get_image_xy(old_item_id))
            old_item_id = item_id

        self._reconfig_scroll()

    def _get_image_xy(self, item_id: int):
        if not item_id:
            return 0, 0

        x = self.canvas.bbox(item_id)[2] + 10
        y = 0

        return x, y

    def add_image(self, image_struct: ImageStruct):
        if not image_struct:
            return

        img = image_struct.copy()

        last_item_id = None
        if len(self.image_dict) > 0:
            last_item_id = self.image_dict.get_last_key()

        img.scale(self.image_dict.scale_ratio)

        item_id = self.canvas.create_image(
            self._get_image_xy(last_item_id), anchor='nw',
            image=img.photoimage, tags='status')
        logger.debug(f'image xy: {self._get_image_xy(last_item_id)}')
        self.image_dict[item_id] = img

        self._reconfig_scroll()

    def _reconfig_scroll(self):
        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲
        logger.debug(self.canvas.bbox("all"))

    def _scroll_y(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

    def _scroll_x(self, event):
        if event.delta > 0:
            self.canvas.xview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.xview_scroll(1, 'units')

    def clear(self, event):
        scale = self.image_dict.scale_ratio
        self.image_dict = ImageStructDict()
        self.image_dict.scale(scale)
