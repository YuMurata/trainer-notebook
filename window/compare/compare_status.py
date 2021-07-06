import tkinter as tk
from tkinter import ttk
from snip import ImageSnipper
from .compare_frame import CompareFrame, StatusFunc
from .status_frame import StatusFrame
from .delete_frame import ControlFrame, ControlFunc
from .select_frame import SelectFrame


class CompareStatusFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        snipper = ImageSnipper()

        frame = ttk.Frame(self)
        compare_frame = CompareFrame(self)
        status_frame = StatusFrame(frame, compare_frame.add_image)
        select_frame = SelectFrame(
            frame, snipper, status_frame.select_image, compare_frame.add_image)
        delete_frame = ControlFrame(self, ControlFunc(select_frame.new_status,
                                                      select_frame.all_delete_umaframe,
                                                      status_frame.clear,
                                                      compare_frame.clear))

        compare_frame.set_status_func(StatusFunc(status_frame.change_image))

        frame.pack(fill=tk.BOTH, expand=True)
        select_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        status_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        compare_frame.pack(fill=tk.X, expand=True)
        delete_frame.pack(fill=tk.BOTH, expand=True)
