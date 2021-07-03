from TeamStadiumInfoDetection.app_linked import AppLinkedThread
from typing import Callable, Dict
import tkinter as tk
from tkinter import ttk, messagebox
from TeamStadiumInfoDetection import Dispatcher
from window.app import BaseApp
from .treeview import ScoreTree, Content
from .fix_frame import FixScoreFrame
from . import fix_frame
from logger import init_logger

logger = init_logger(__name__)


class ScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, metrics_updater: Callable[[], None]):
        super().__init__(master)

        self.metrics_updater = metrics_updater
        self.content_dict: Dict[str, Dict[str, int]] = dict()

        self.treeview_score = ScoreTree(self)
        self.treeview_score.bind('<<UpdateApp>>', self.update_app)
        self.treeview_score.bind('<<TreeviewSelect>>', self._select_item)

        self.treeview_score.pack()

        self.fix_score_frame = FixScoreFrame(self)
        self.fix_score_frame.set_callback(
            fix_frame.Callback(self._fix_content))
        self.fix_score_frame.pack(expand=True, fill=tk.BOTH)

        self._create_button().pack()

        def generate_update_app():
            self.treeview_score.event_generate('<<UpdateApp>>', when='tail')
        self.linked_thread = AppLinkedThread(Dispatcher(generate_update_app))
        self.linked_thread.start()

    def _fix_content(self, content: Content):
        if not content.name:
            messagebox.showerror('error', '名前が入力されていません！')
            return

        id_list = self.treeview_score.selection()

        if not id_list or len(id_list) <= 0:
            return

        select_id = id_list[0]
        self.treeview_score.fix(select_id, content)

    def _select_item(self, event: tk.Event):
        id_list = self.treeview_score.selection()

        if not id_list or len(id_list) <= 0:
            return

        select_id = id_list[0]
        select_item = self.treeview_score.set(select_id)

        content = Content(name=select_item['Name'],
                          rank=select_item['Rank'],
                          score=select_item['Score'])
        self.fix_score_frame.set_value(content)
        self.treeview_score.select_item = content

    def update_app(self, event):
        self.content_dict = self.linked_thread.get()

        content_list = [Content(name, content.get('rank', None),
                                content.get('score', None))
                        for name, content in self.content_dict.items()]

        self.treeview_score.clear()
        self.treeview_score.fill(content_list)

    def destroy(self) -> None:
        self.linked_thread.stop()
        return super().destroy()

    def deleteResultReadScore(self):
        self.linked_thread.init_dict()
        self.treeview_score.event_generate('<<UpdateApp>>', when='tail')

    def _create_button(self):
        frame = ttk.Frame(self)
        frame.pack()

        self.button_reset = ttk.Button(frame)
        self.button_reset.configure(text="削除")
        self.button_reset.configure(command=self.deleteResultReadScore)
        self.button_reset.pack(side=tk.LEFT)

        # Button
        self.button_register = ttk.Button(frame)
        self.button_register.configure(text="登録")
        self.button_register.configure(
            command=self._regist)
        self.button_register.pack(side=tk.RIGHT)

        return frame

    def _regist(self):
        self.linked_thread.overwrite_umainfo_file()
        self.metrics_updater()


class ScoreApp(BaseApp):
    def __init__(self, master: tk.Toplevel, master_updater) -> None:
        def generator():
            window = tk.Toplevel(master)
            frame = ScoreFrame(window, master_updater)
            frame.pack()
            return window
        target_size = (300, 500)
        super().__init__(generator, master, target_size)
