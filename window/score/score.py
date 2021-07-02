from TeamStadiumInfoDetection.app_linked import AppLinkedThread
from typing import Callable, Dict, Tuple
import tkinter as tk
from tkinter import ttk
from TeamStadiumInfoDetection import Dispatcher
from window.app import BaseApp
from .treeview import ScoreTree
from .treeview import ScoreTree, Content
from .fix_frame import FixScoreFrame
from logger import init_logger

logger = init_logger(__name__)


class ScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, metrics_updater: Callable[[], None]):
        super().__init__(master)

        self.treeview_score = ScoreTree(self)
        self.treeview_score.bind('<<UpdateApp>>', self.update_app)
        self.treeview_score.bind('<<TreeviewSelect>>', self._select_item)
        def generate_update_app():
            self.treeview_score.event_generate('<<UpdateApp>>', when='tail')

        self.linked_thread = AppLinkedThread(Dispatcher(generate_update_app))
        self.linked_thread.start()

        self._create_widgets()
        self.metrics_updater = metrics_updater
        self.content_dict: Dict[str, Dict[str, int]] = dict()

            return




    def update_app(self, event):
        self.content_dict = self.linked_thread.get()


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
