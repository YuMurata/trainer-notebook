import cv2
from snip import ImageSnipper
from misc import pil2cv
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from typing import Callable, NamedTuple, List
from logger import init_logger
from compare_window.image import ImageStruct


class DeleteFunc(NamedTuple):
    list_delete: Callable[[], None]
    status_view_delete: Callable[[], None]
    compare_view_delete: Callable[[], None]


class DeleteFrame(tk.Frame):
    def __init__(self, master: tk.Widget, delete_func: DeleteFunc):
        super().__init__(master)

        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT, pady=5, fill=tk.BOTH, expand=True)
        self.all_delete_button = ttk.Button(frame, text='all_delete')
        self.all_delete_button.bind(
            '<Button-1>', self.all_delete_button_left_click)
        self.all_delete_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.all_view_delete_button = ttk.Button(frame, text='all_view_clear')
        self.all_view_delete_button.bind(
            '<Button-1>', self.all_view_delete_button_left_click)
        self.all_view_delete_button.pack(
            side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.compare_view_delete_button = ttk.Button(
            frame, text='compare_view_clear')
        self.compare_view_delete_button.bind(
            '<Button-1>', self.compare_view_delete_button_left_click)
        self.compare_view_delete_button.pack(
            side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.delete_func = delete_func

    def all_delete_button_left_click(self, event):
        for func in self.delete_func:
            func(event)

    def all_view_delete_button_left_click(self, event):
        self.delete_func.status_view_delete(event)
        self.delete_func.compare_view_delete(event)

    def compare_view_delete_button_left_click(self, event):
        self.delete_func.compare_view_delete(event)
