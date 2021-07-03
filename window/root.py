import tkinter as tk
from tkinter import ttk
from enum import IntEnum, auto
from .team_stadium.metrics.graph import GraphView
from uma_info import UmaInfo, UmaPointFileIO
from typing import List
from .screenshot import ScreenShotFrame
from .compare import CompareStatusFrame
from .team_stadium.score import ScoreFrame
from .team_stadium.metrics import MetricsView


class Win1(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # self.master.geometry("500x400")
        self.master.resizable(False, False)
        self.master.title("umauma drive")

        self.tab = ttk.Notebook(self, height=-1, width=-1)
        self.tab.pack(fill=tk.BOTH, expand=True)

        self.graph_view = GraphView()
        team_stadium = ttk.Notebook(self, height=-1, width=-1)
        self.metrics_view = MetricsView(team_stadium)
        # self.tab.add(self.metrics_view, text='Metrics')
        team_stadium.add(ScoreFrame(
            self, self.metrics_view.generate_update), text='rank-score')
        team_stadium.add(self.metrics_view, text='metrics')
        team_stadium.add(ttk.Label(self, text='graph'), text='graph')
        self.tab.add(team_stadium, text='TeamStadium')
        self.tab.add(CompareStatusFrame(self), text='Status')
        self.tab.add(ScreenShotFrame(self), text='Screenshot')
        # self.score_app = ScoreApp(master, self.metrics_view.generate_update)
        # self.graph_app = GraphApp(master, self.graph_view)
        # self.create_widgets()

        # def lift_app(event):
        #     self.score_app.lift()
        #     self.graph_app.lift()
        #     master.lift()

        # self.tab = ttk.Notebook(self, height=-1, width=-1)
        # self.tab.pack(fill=tk.BOTH, expand=True)

        # self.graph_view = GraphView()
        # team_stadium = ttk.Notebook(self, height=-1, width=-1)
        # self.metrics_view = MetricsView(team_stadium)
        # # self.tab.add(self.metrics_view, text='Metrics')
        # team_stadium.add(ttk.Label(self, text='rank-score'), text='rank-score')
        # team_stadium.add(self.metrics_view, text='metrics')
        # self.tab.add(team_stadium, text='TeamStadium')
        # self.tab.add(ttk.Label(self, text='Status'), text='Status')
        # self.tab.add(ScreenShotFrame(self), text='Screenshot')
        # self.score_app = ScoreApp(master, self.metrics_view.generate_update)
        # self.graph_app = GraphApp(master, self.graph_view)
        # self.create_widgets()

        # def lift_app(event):
        #     self.score_app.lift()
        #     self.graph_app.lift()
        #     master.lift()

        # def icon_app(event):
        #     self.score_app.iconify()
        #     self.graph_app.iconify()

        # def deicon_app(event):
        #     self.score_app.deiconify()
        #     self.graph_app.deiconify()

        # master.bind('<FocusIn>', lift_app)
        # master.bind('<Unmap>', icon_app)
        # master.bind('<Map>', deicon_app)
        # self.metrics_view.generate_update()

    def create_widgets(self):
        # Button
        self.button_new_win2 = ttk.Button(self)
        self.button_new_win2.configure(text="regist score")
        self.button_new_win2.configure(command=self.score_app.Activate)

        self.button_new_win3 = ttk.Button(self)
        self.button_new_win3.configure(text="disp graph")
        self.button_new_win3.configure(command=self.graph_app.Activate)

        # self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.button_new_win2.pack()
        self.button_new_win3.pack()

        self.metrics_view.set_graph_updater(self.graph_app.update_canvas)
        # self.metrics_view.pack()

    def destroy(self) -> None:
        ret = super().destroy()
        # self.score_app.close_window()
        # self.graph_app.close_window()
        return ret
