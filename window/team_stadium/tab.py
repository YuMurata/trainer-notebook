from TeamStadiumInfoDetection.thread_closer import ThreadCloser
from TeamStadiumInfoDetection.dispatcher import Dispatcher
from TeamStadiumInfoDetection.app_linked import AppLinkedThread
import threading
from exception import IllegalInitializeException
from logger import CustomLogger
import tkinter as tk
from tkinter import ttk
from typing import Callable, List
from uma_info.uma_info import UmaInfo
from .score import ScoreFrame
from .metrics.treeview import TreeViewFrame
from .metrics.graph import GraphFrame


logger = CustomLogger(__name__)


class ReadScoreWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget, linked_thread: AppLinkedThread,
                 metrics_updater: Callable[[], None]):
        super().__init__(master, name='read_score')

        self.linked_thread = linked_thread
        score_frame = ScoreFrame(self, self.linked_thread)
        self.linked_thread.set_dispatcher(
            Dispatcher(score_frame.generate_update_app))
        logger.debug('--- activate ---')
        self.linked_thread.activate()
        logger.debug(f'thread: {threading.enumerate()}')
        score_frame.set_metrics_updater(metrics_updater)
        score_frame.pack()

    def destroy(self) -> None:
        logger.debug('--- deactivate ---')
        with logger.scope('init'):
            self.linked_thread.init_dict()
        self.linked_thread.deactivate()
        return super().destroy()


class ScoreWindowManager:
    def __init__(self, master: tk.Widget) -> None:
        self.master = master
        self.win: tk.Toplevel = None
        self.metrics_updater: Callable[[], None] = None

        self.linked_thread = AppLinkedThread()
        ThreadCloser([self.linked_thread]).start()
        self.linked_thread.start()

    def activate(self):
        if not self.metrics_updater:
            raise IllegalInitializeException('not set metrics_updater')

        if self.win and self.win.winfo_exists():
            logger.debug('win exists')
            self.win.deiconify()
            self.win.lift()
            return

        self.win = ReadScoreWindow(
            self.master, self.linked_thread, self.metrics_updater)

    def set_metrics_updater(self, metrics_updater: Callable[[None], None]):
        self.metrics_updater = metrics_updater


class Metrics_GraphFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        frame = ttk.Frame(self)
        self.treeview_frame = TreeViewFrame(frame)
        treeview_score = self.treeview_frame.treeview_score
        self.metrics_updater = treeview_score.generate_update
        button = ttk.Button(frame, text='read score')

        self.score_manager = ScoreWindowManager(self)
        self.score_manager.set_metrics_updater(self.metrics_updater)

        button.bind('<ButtonRelease-1>',
                    lambda e: self.score_manager.activate())
        self.treeview_frame.pack()
        button.pack()
        self.graph_frame = GraphFrame(self)

        self.graph_updater = self.graph_frame.canvas.update_uma_info_list

        self.treeview_frame.treeview_score.set_graph_updater(
            self.graph_updater)

        frame.pack(side=tk.LEFT)
        self.graph_frame.pack(side=tk.LEFT)

    def get_graph_updater(self) -> Callable[[List[UmaInfo]], None]:
        return self.graph_updater

    def get_metrics_updater(self) -> Callable[[], None]:
        return self.metrics_updater
