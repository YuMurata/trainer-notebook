import tkinter as tk
from tkinter import ttk
from snip import ImageSnipper
from compare_window.compare_frame import CompareFrame
from compare_window.status_frame import StatusFrame
from .select_frame import SelectFrame


class CompareApp(tk.Toplevel):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        snipper = ImageSnipper()

        # app = WinStatusComparison(master=root)
        frame = ttk.Frame(self)
        compare_frame = CompareFrame(self)
        status_frame = StatusFrame(frame, compare_frame.add_image)
        select_frame = SelectFrame(
            frame, snipper, status_frame.select_image)

        frame.pack()
        select_frame.pack(side=tk.LEFT, fill=tk.Y)
        status_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        compare_frame.pack(fill=tk.X, expand=True)
