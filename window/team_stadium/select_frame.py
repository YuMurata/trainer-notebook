import tkinter as tk
from tkinter import ttk
from enum import Enum


class SelectKey(Enum):
    SCORE = 'score'
    RANK = 'rank'


class SelectFrame(ttk.Labelframe):
    def __init__(self, master: tk.Widget):
        super().__init__(master, text='select info')
        self.select_value = tk.StringVar(self, value=SelectKey.SCORE.value)
        ttk.Radiobutton(self, text='score', value=SelectKey.SCORE.value,
                        variable=self.select_value).pack(side=tk.LEFT)
        ttk.Radiobutton(self, text='rank', value=SelectKey.RANK.value,
                        variable=self.select_value).pack(side=tk.LEFT)

    def get(self):
        self.select_value.get()
