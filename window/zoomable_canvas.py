import tkinter as tk
from .scrollable_canvas import ScrollableCanvasFrame
from .image import ImageStructDict
from typing import Callable, Tuple

GetImageXY = Callable[[int], Tuple[int, int]]


class ZoomableCanvasFrame(ScrollableCanvasFrame):
    def __init__(self, master: tk.Widget, image_dict: ImageStructDict,
                 get_image_xy: GetImageXY, *,
                 canvas_option: dict):
        super().__init__(master, canvas_option=canvas_option)
        self.canvas.bind('<Control-MouseWheel>', self._zoom)
        self.image_dict = image_dict
        self.get_image_xy = get_image_xy

    def _zoom(self, event: tk.Event):
        step = 0.25 if event.delta > 0 else -0.25

        self.image_dict.step_scale(step)

        old_item_id = None
        for item_id in self.image_dict.keys():
            photoimage = self.image_dict[item_id].photoimage
            self.canvas.itemconfig(item_id, image=photoimage)
            self.canvas.moveto(item_id, *self.get_image_xy(old_item_id))
            old_item_id = item_id

        self.reconfig_scroll()

    def canvas_xy(self, event: tk.Event) -> Tuple[int, int]:
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
