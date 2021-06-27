from typing import Callable
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from logger import init_logger

logger = init_logger(__name__)


class StatusFrame(ttk.Frame):
    def __init__(self, master: tk.Widget,
                 add_compare_image: Callable[[ImageTk.PhotoImage], None]):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=400, height=300)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.photoimage: ImageTk.PhotoImage = None
        self.image_id: int = None

        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.config(command=self.canvas.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.scroll.set)
        self.canvas.bind("<MouseWheel>", self._scroll_y)
        self.canvas.bind(
            '<Button-1>', lambda _: add_compare_image(self.photoimage))

    def select_image(self, image: Image.Image):
        self.photoimage = ImageTk.PhotoImage(image=image)

        if not self.image_id:
            self.canvas.create_image(
                0, 0, anchor='nw', image=self.photoimage)
        else:
            self.canvas.itemconfig(self.image_id, image=self.photoimage)

        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲

    def _scroll_y(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')
