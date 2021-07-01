import tkinter as tk
from tkinter import ttk
from typing import Tuple, Dict, List
from snip import ImageSnipper
from window.image import Emphasis, ImageStruct, ImageStructDict
from window.zoomable_canvas import ZoomableCanvasFrame
from .name_change import NameChangeFrame
from PIL import Image
from .define import screenshot_dir


class ViewFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self.name_change_frame = NameChangeFrame(self)
        self.name_change_frame.set_load_image(self.load_image)
        self.name_change_frame.pack()

        width, height = ImageSnipper.snip_size
        width *= 2.2

        self.image_dict = ImageStructDict()
        self.name_dict: Dict[int, str] = dict()

        self.canvas_frame = ZoomableCanvasFrame(
            self, self.image_dict, self._get_image_xy,
            canvas_option={'bg': 'white', 'width': width, 'height': height})
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = self.canvas_frame.canvas
        self.canvas.tag_bind('screenshot', '<Button-1>', self._get_image_name)

        self.load_image()
        self.prev_id: int = None

    def _get_image_name(self, event: tk.Event):
        x, y = self.canvas_frame.canvas_xy(event)

        item_id_list: List[int] = self.canvas.find_closest(x, y)

        if len(item_id_list) < 1:
            return

        item_id = item_id_list[0]

        if self.prev_id:
            prev_image = self.image_dict[self.prev_id]
            prev_image.set_emphasis(None)
            self.canvas.itemconfig(self.prev_id, image=prev_image.photoimage)

        image_struct = self.image_dict[item_id]
        image_struct.set_emphasis(Emphasis(3, (0, 200, 0)))
        self.canvas.itemconfig(item_id, image=image_struct.photoimage)

        image_name = self.name_dict[item_id]
        self.name_change_frame.set_image_name(image_name)

        self.prev_id = item_id

    def load_image(self):
        for item_id in self.image_dict.keys():
            self.canvas.delete(item_id)

        self.image_dict.clear()
        self.name_dict.clear()

        old_item_id: int = None
        for image_path in screenshot_dir.iterdir():
            if image_path.suffix != '.png':
                continue

            image_struct = ImageStruct(Image.open(image_path))

            item_id = self.canvas.create_image(self._get_image_xy(
                old_item_id), anchor=tk.NW, image=image_struct.photoimage,
                tags='screenshot')
            old_item_id = item_id

            self.image_dict[item_id] = image_struct
            self.name_dict[item_id] = image_path.stem

        self.canvas_frame.reconfig_scroll()
        self.prev_id = None

    def _get_image_xy(self, item_id: int) -> Tuple[int, int]:
        if not item_id:
            return 0, 0

        pad = 10

        x = self.canvas.bbox(item_id)[2] + pad
        y = self.canvas.bbox(item_id)[1]

        threshold_x = 700
        if x > threshold_x:
            x = 0
            y = self.canvas.bbox(item_id)[3]+pad

        return x, y
