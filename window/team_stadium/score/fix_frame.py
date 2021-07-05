import tkinter as tk
from tkinter import ttk
from typing import Callable,  NamedTuple
from logger import CustomLogger
from .treeview import Content, ignore_score
from exception import IllegalInitializeException
from uma_info import UmaNameFileReader

logger = CustomLogger(__name__)


class Callback(NamedTuple):
    fix: Callable[[Content], None]


class FocusObserber:
    def __init__(self) -> None:
        self.has_focus = False

    def focus_in(self):
        self.has_focus = True

    def focus_out(self):
        self.has_focus = False

    def get(self):
        return self.has_focus


class RankFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        width = 10

        label = ttk.Label(self, text='rank', width=width)
        label.pack()

        self.rank = tk.StringVar(self)
        rank_list = list(range(1, 12+1))

        def validate(P: str):
            if P == '':
                return True

            if not P.isdecimal():
                return False

            rank = int(P)
            return rank in rank_list

        val_cmd = (self.register(validate), '%P')
        self.combo = ttk.Combobox(self, textvariable=self.rank, width=width,
                                  values=rank_list, validatecommand=val_cmd,
                                  validate='key')

        self.combo_focus = FocusObserber()
        self.combo.bind('<FocusIn>', lambda e: self.combo_focus.focus_in())
        self.combo.bind('<FocusOut>', lambda e: self.combo_focus.focus_out())
        self.combo.pack()

    def get_text(self):
        rank = self.rank.get()
        return int(rank) if rank.isdecimal() else None

    def set_text(self, rank: str):
        self.rank.set(rank)


class NameFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        width = 20

        label = ttk.Label(self, text='name', width=width)
        label.pack()

        uma_name_list = UmaNameFileReader.Read()
        self.name = tk.StringVar(self)
        self.entry = ttk.Combobox(self, textvariable=self.name,
                                  width=width, values=uma_name_list)

        self.entry_focus = FocusObserber()
        self.entry.bind('<FocusIn>', lambda e: self.entry_focus.focus_in())
        self.entry.bind('<FocusOut>', lambda e: self.entry_focus.focus_out())
        self.entry.pack()

    def get_text(self):
        return self.name.get()

    def set_text(self, name: str):
        self.name.set(name)


class ScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        width = 10

        label = ttk.Label(self, text='score', width=width)
        label.pack()

        self.score = tk.StringVar(self)

        def validate(P: str):
            if P == '':
                return True

            return P.isdecimal()

        val_cmd = (self.register(validate), '%P')
        self.combo = ttk.Entry(self, textvariable=self.score, width=width,
                               validatecommand=val_cmd,
                               validate='key')

        self.combo_focus = FocusObserber()
        self.combo.bind('<FocusIn>', lambda e: self.combo_focus.focus_in())
        self.combo.bind('<FocusOut>', lambda e: self.combo_focus.focus_out())
        self.combo.pack()

    def get_text(self):
        score = self.score.get()
        return int(score) if score.isdecimal() else None

    def set_text(self, score: str):
        self.score.set(score)


class FixScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        frame = ttk.Frame(self)
        frame.pack()

        bind_return_cmd = ('<Return>', self._fix_content)

        self.rank_frame = RankFrame(frame)
        self.rank_frame.combo.bind(*bind_return_cmd)
        self.rank_frame.pack(side=tk.LEFT, padx=3)

        self.name_frame = NameFrame(frame)
        self.name_frame.entry.bind(*bind_return_cmd)
        self.name_frame.pack(side=tk.LEFT, padx=3)

        self.score_frame = ScoreFrame(frame)
        self.score_frame.combo.bind(*bind_return_cmd)
        self.score_frame.pack(side=tk.LEFT, padx=3)

        button_frame = ttk.Frame(self)
        button_frame.pack()

        fix_button = ttk.Button(button_frame, text='fix')
        fix_button.bind('<Button-1>', self._fix_content)
        fix_button.pack(side=tk.LEFT, padx=3)

        delete_button = ttk.Button(button_frame, text='delete')
        delete_button.bind('<Button-1>', self._delete_content)
        delete_button.pack(side=tk.LEFT, padx=3)

        self.callback: Callback = None

    def set_value(self, content: Content):
        if any([self.rank_frame.combo_focus.get(),
                self.name_frame.entry_focus.get(),
                self.score_frame.combo_focus.get()]):
            return
        self.rank_frame.set_text(content.rank)
        self.name_frame.set_text(content.name)
        self.score_frame.set_text(content.score)

    def set_callback(self, callback: Callback):
        self.callback = callback

    def _fix_content(self, event: tk.Widget):
        if not self.callback:
            raise IllegalInitializeException('not set callback')

        content = Content(name=self.name_frame.get_text(),
                          rank=self.rank_frame.get_text(),
                          score=self.score_frame.get_text())
        self.callback.fix(content)

    def _delete_content(self, event: tk.Widget):
        if not self.callback:
            raise IllegalInitializeException('not set callback')

        content = Content(name=self.name_frame.get_text(),
                          rank=self.rank_frame.get_text(),
                          score=ignore_score)
        self.callback.fix(content)
