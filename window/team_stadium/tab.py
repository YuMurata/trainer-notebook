from exception import IllegalInitializeException
from logger import CustomLogger
import tkinter as tk
from tkinter import ttk
from typing import Callable, List
from uma_info.uma_info import UmaInfo
from .score import ScoreFrame
from .metrics.treeview import TreeViewFrame
from .metrics.graph import GraphFrame
from window.team_stadium import score

logger = CustomLogger(__name__)


class ScoreWindowManager:
    def __init__(self, master: tk.Widget) -> None:
        self.master = master
        self.win: tk.Toplevel = None
        self.metrics_updater: Callable[[], None] = None

    def activate(self):
        if not self.metrics_updater:
            raise IllegalInitializeException('not set metrics_updater')

        if self.win and self.win.winfo_exists():
            logger.debug('win exists')
            self.win.deiconify()
            self.win.lift()
            return

        self.win = tk.Toplevel(self.master)
        score_frame = ScoreFrame(self.win)
        score_frame.set_metrics_updater(self.metrics_updater)
        score_frame.pack()

    def set_metrics_updater(self, metrics_updater: Callable[[None], None]):
        self.metrics_updater = metrics_updater


class Metrics_GraphFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        frame = ttk.Frame(self)
        self.treeview_frame = TreeViewFrame(frame)
        self.metrics_updater = self.treeview_frame.treeview_score.generate_update
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


class TeamStadiumNotebook(ttk.Notebook):
    def __init__(self, master: tk.Widget):
        super().__init__(master, height=-1, width=-1)
        score_metrics_frame = Score_MetricsFrame(self)
        metrics_graph_frame = Metrics_GraphFrame(self)

        score_metrics_frame.set_graph_updater(
            metrics_graph_frame.get_graph_updater())

        score_metrics_frame.set_metrics_updater(
            metrics_graph_frame.get_metrics_updater())

        self.add(score_metrics_frame, text='score-metrics')
        self.add(metrics_graph_frame, text='metrics-graph')

        self.sm_treeview = score_metrics_frame.treeview_frame.treeview_score
        self.mg_treeview = metrics_graph_frame.treeview_frame.treeview_score

        # self.sm_treeview.bind('<<TreeviewSelect>>',
        #                       self._sync_mg_treeview_selection, True)
        # self.mg_treeview.bind('<<TreeviewSelect>>',
        #                       self._sync_sm_treeview_selection, True)

    def _sync_mg_treeview_selection(self, event):
        sm_selection_list = self.sm_treeview.selection()
        mg_selection_list = self.mg_treeview.selection()

        if sm_selection_list == mg_selection_list:
            return

        self.mg_treeview.selection_set(sm_selection_list)

    def _sync_sm_treeview_selection(self, event):
        sm_selection_list = self.sm_treeview.selection()
        mg_selection_list = self.mg_treeview.selection()

        if sm_selection_list == mg_selection_list:
            return
        self.sm_treeview.selection_set(mg_selection_list)
