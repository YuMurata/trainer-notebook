import tkinter as tk
from tkinter import ttk
from logger import init_logger

logger = init_logger(__name__)


class FixScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        option_dict = {'rank': dict(width=10),
                       'name': dict(width=20),
                       'score': dict(width=10), }

        key_list = list(option_dict.keys())
        self.entry_var_dict = {key: tk.StringVar(self) for key in key_list}

        entry_frame = ttk.Frame(self)
        for key, option in option_dict.items():
            self._create_entry(entry_frame, key, option).pack(
                side=tk.LEFT, padx=3)
        entry_frame.pack()

        button = ttk.Button(self, text='fix')
        button.pack()

    def _create_entry(self, master: tk.Widget, key: str, option: dict):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=key, **option)
        entry = ttk.Entry(
            frame, textvariable=self.entry_var_dict[key], **option)

        label.pack()
        entry.pack()

        return frame
