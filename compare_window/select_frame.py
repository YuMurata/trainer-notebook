from typing import Callable
from snip import ImageSnipper
from PIL import Image
import tkinter as tk
from tkinter import ttk
from logger import init_logger
from compare_window.list_frame import ListFrame

logger = init_logger(__name__)


class SelectFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, snipper: ImageSnipper,
                 show_image: Callable[[Image.Image], None]):
        super().__init__(master)

        self.list_frame = ListFrame(self, snipper, show_image)
        self.list_frame.pack(fill=tk.Y, expand=True)

        all_delete_button = ttk.Button(self, text='all_delete')
        all_delete_button.pack(fill=tk.X)
        all_delete_button.bind(
            '<Button-1>', self.list_frame.all_delete_umaframe)
