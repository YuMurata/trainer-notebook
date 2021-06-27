import tkinter as tk
from tkinter import ttk
from snip import ImageSnipper
from compare_window.compare_frame import CompareFrame, StatusFunc
from compare_window.status_frame import StatusFrame
from .select_frame import SelectFrame

# 開発用にcompareappをメインウィンドウにしてる
# 開発終わったらtoplevelに戻す

# class CompareApp(tk.Toplevel):


class CompareApp(tk.Tk):
    def __init__(self, master: tk.Widget):
        # super().__init__(master)
        super().__init__()
        snipper = ImageSnipper()

        # app = WinStatusComparison(master=root)
        frame = ttk.Frame(self)
        compare_frame = CompareFrame(self)
        status_frame = StatusFrame(frame, compare_frame.add_image)
        select_frame = SelectFrame(
            frame, snipper, status_frame.select_image)

        compare_frame.set_status_func(StatusFunc(status_frame.change_image))

        frame.pack()
        select_frame.pack(side=tk.LEFT, fill=tk.Y)
        status_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        compare_frame.pack(fill=tk.X, expand=True)
