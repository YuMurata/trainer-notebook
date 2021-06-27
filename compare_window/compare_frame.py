from exception import IllegalInitializeException
from typing import Callable, Dict, List, NamedTuple
from PIL import ImageTk
import tkinter as tk
from tkinter import ttk
from logger import init_logger

logger = init_logger(__name__)


class StatusFunc(NamedTuple):
    change: Callable[[ImageTk.PhotoImage], ImageTk.PhotoImage]


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

        self.canvas.tag_bind('status', '<Button-1>', self._change_image)
        self.canvas.tag_bind('status', '<Button-3>', self._delete_image)

        self.image_dict: Dict[int, ImageTk.PhotoImage] = dict()
        self.status_func: StatusFunc = None

    def set_status_func(self, status_func: StatusFunc):
        self.status_func = status_func

    def _change_image(self, event: tk.Event):
        if not self.status_func:
            raise IllegalInitializeException('status_func is not initialized')

        item_id_list: List[int] = self.canvas.find_closest(event.x, event.y)

        if len(item_id_list) < 1:
            return

        item_id = item_id_list[0]

        if item_id not in self.image_dict:
            return

        photoimage = self.status_func.change(self.image_dict[item_id])
        self.canvas.itemconfig(item_id, image=photoimage)
        self.image_dict[item_id] = photoimage

        self._reconfig_scroll()

    def _delete_image(self, event: tk.Event):
        item_id_list: List[int] = self.canvas.find_closest(event.x, event.y)

        if len(item_id_list) < 1:
            return

        item_id = item_id_list[0]

        if item_id not in self.image_dict:
            return

        self.image_dict.pop(item_id)
        self.canvas.delete(item_id)

        for i, item_id in enumerate(self.image_dict.keys()):
            self.canvas.moveto(item_id, *self._get_image_xy(i))

        self._reconfig_scroll()

    def _get_image_xy(self, image_idx: int):
        image_width = 400  # temp
        x = image_idx*(image_width+10)
        y = 0

        return x, y

    def add_image(self, photoimage: ImageTk.PhotoImage):
        if not photoimage:
            return
        item_id = self.canvas.create_image(
            self._get_image_xy(len(self.image_dict)), anchor='nw',
            image=photoimage, tags='status')
        logger.debug(f'image xy: {self._get_image_xy(len(self.image_dict))}')
        self.image_dict[item_id] = photoimage

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
