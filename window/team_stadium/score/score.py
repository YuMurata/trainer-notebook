import threading
from uma_info import UmaPointFileIO
from TeamStadiumInfoDetection.app_linked import AppLinkedThread
from typing import Callable, List
import tkinter as tk
from tkinter import ttk, messagebox
from window.app import BaseApp
from .treeview import ScoreTree, Content, ignore_score
from .fix_frame import FixScoreFrame
from . import fix_frame
from logger import CustomLogger
from exception import IllegalInitializeException

logger = CustomLogger(__name__)


class ScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, linked_thread: AppLinkedThread):
        super().__init__(master)

        self.metrics_updater: Callable[[], None] = None

        self.treeview_score = ScoreTree(self)
        self.treeview_score.bind('<<UpdateApp>>', self.update_app)
        self.treeview_score.bind('<<TreeviewSelect>>', self._select_item)

        self.treeview_score.pack()

        self.fix_score_frame = FixScoreFrame(self)
        self.fix_score_frame.set_callback(
            fix_frame.Callback(self._fix_content))
        self.fix_score_frame.pack(expand=True, fill=tk.BOTH)

        self._create_button().pack()

        self.linked_thread = linked_thread

    def generate_update_app(self):
        if not threading.main_thread().is_alive():
            return

        if not self.treeview_score.winfo_exists():
            return

        with logger.scope('generate'):
            try:
                self.treeview_score.event_generate(
                    '<<UpdateApp>>', when='tail')
            except tk.TclError as e:
                logger.error(str(e))

    def set_metrics_updater(self, metrics_updater: Callable[[], None]):
        self.metrics_updater = metrics_updater

    def _fix_content(self, content: Content):
        if not content.name:
            messagebox.showerror('error', '名前が入力されていません！', parent=self)
            return

        id_list = self.treeview_score.selection()

        if not id_list or len(id_list) <= 0:
            return

        select_id = id_list[0]
        if content.score == ignore_score:
            self.treeview_score.selection_remove(select_id)

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
        with logger.scope('get score'):
            read_content_dict = self.linked_thread.get()
        treeview_content_dict = {content.name: dict(
            rank=content.rank, score=content.score)
            for content in self.treeview_score.content_dict.values()}

        name_set = set(list(read_content_dict.keys()) +
                       list(treeview_content_dict.keys()))

        def get_read_content(name: str) -> Content:
            read_content = read_content_dict.get(name, None)
            if not read_content:
                return Content(None, None, None)

            rank = read_content.get('rank', None)
            score = read_content.get('score', None)
            return Content(name, rank, score)

        def choose_content(name: str) -> Content:
            read_content = get_read_content(name)

            treeview_content = treeview_content_dict.get(name, None)
            if not treeview_content:
                return read_content

            rank = treeview_content['rank']
            if not rank:
                rank = read_content.rank

            score = treeview_content['score']
            if not score:
                score = read_content.score

            return Content(name, rank, score)

        content_list = [choose_content(name) for name in name_set if name]

        self.fix_score_frame.set_value(Content('', '', ''))

        self.treeview_score.clear()
        self.treeview_score.fill(content_list)

    def deleteResultReadScore(self):
        self.linked_thread.init_dict()
        self.treeview_score.clear()
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
        def is_valid_content_list(content_list: List[Content]):
            def is_valid_content(content: Content):
                return all(content)
            return all([is_valid_content(content) for content in content_list])

        def extract_content_list(content_list: List[Content]):
            def is_extractable(content: Content):
                return content.score and content.score != ignore_score
            return [content for content in content_list
                    if is_extractable(content)]
        content_list = extract_content_list(
            list(self.treeview_score.content_dict.values()))
        if not is_valid_content_list(content_list):
            messagebox.showerror('error', 'スコアが正しく入力されていません', parent=self)
            return

        uma_info_dict = UmaPointFileIO.Read()
        for content in content_list:
            uma_info_dict[content.name].add_rank(content.rank)
            uma_info_dict[content.name].add_score(content.score)

        UmaPointFileIO.Write(uma_info_dict)

        if not self.metrics_updater:
            raise IllegalInitializeException('not set metrics_updater')
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
