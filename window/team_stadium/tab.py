import tkinter as tk
from tkinter import ttk
from typing import Callable, List
from uma_info.uma_info import UmaInfo
from .score import ScoreFrame
from .metrics.treeview import TreeViewFrame
from .metrics.graph import GraphFrame


class Score_MetricsFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        self.score_frame = ScoreFrame(self)
        self.treeview_frame = TreeViewFrame(self)

        self.score_frame.pack(side=tk.LEFT)
        self.treeview_frame.pack(side=tk.LEFT)

    def set_graph_updater(self,
                          graph_updater: Callable[[List[UmaInfo]], None]):
        self.treeview_frame.treeview_score.set_graph_updater(graph_updater)

    def set_metrics_updater(self, updater):
        def updater_mass():
            updater()
            self.treeview_frame.treeview_score.generate_update()
        self.score_frame.set_metrics_updater(updater_mass)


class Metrics_GraphFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        self.treeview_frame = TreeViewFrame(self)
        self.graph_frame = GraphFrame(self)

        self.graph_updater = self.graph_frame.canvas.update_uma_info_list
        self.metrics_updater = self.treeview_frame.treeview_score.generate_update

        self.treeview_frame.treeview_score.set_graph_updater(
            self.graph_updater)

        self.treeview_frame.pack(side=tk.LEFT)
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

        self.sm_treeview.bind('<<TreeviewSelect>>',
                              self._sync_mg_treeview_selection, True)
        self.mg_treeview.bind('<<TreeviewSelect>>',
                              self._sync_sm_treeview_selection, True)

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
