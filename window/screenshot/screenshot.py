import tkinter as tk
from tkinter import ttk
from .take import TakeFrame
from .view import ViewFrame


class ScreenShotFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self.tab = ttk.Notebook(self, width=-1, height=-1)
        self.tab.pack(expand=True, fill=tk.BOTH)

        take_frame = TakeFrame(self)
        self.tab.add(take_frame, text='take')

        view_frame = ViewFrame(self)
        self.tab.add(view_frame, text='view')

        take_frame.set_load_image(view_frame.load_image)
