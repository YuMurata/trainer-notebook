import tkinter as tk
from tkinter import ttk
from tkinter.constants import BOTTOM
from typing import List
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from Uma import UmaInfo, UmaPointFileIO
from enum import Enum, auto
from colorsys import hsv_to_rgb


class GraphView:
    class DrawTarget(Enum):
        LINE = auto()
        BAR = auto()

    def __init__(self):
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)

        self.fig.subplots_adjust(bottom=0.2, left=0.2)

        self.uma_info_list: List[UmaInfo] = None
        self.draw_target = self.DrawTarget.LINE
        self.update_line()

    def update_line(self):
        self.ax.cla()

        self.ax.set_xlabel('race')
        self.ax.set_ylabel('score')

        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        if self.uma_info_list:
            h_diff = 1.0 / len(self.uma_info_list)
            for i, uma_info in enumerate(self.uma_info_list):
                x = np.arange(len(uma_info.points))+1
                y = np.array(uma_info.points)

                rgb = hsv_to_rgb(h_diff*i, 1, 0.8)

                # ax1
                self.ax.plot(x, y, marker='o',
                             color=rgb, label=uma_info.name)

            self.ax.legend(loc="lower right", fontsize=8,
                           prop={'family': 'Meiryo'})

    def update_bar(self):
        self.ax.cla()

        self.ax.set_xlabel('name')
        self.ax.set_ylabel('mean score')

        self.ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        if self.uma_info_list:
            name_list = [uma_info.name for uma_info in self.uma_info_list]
            mean_list = [uma_info.Mean for uma_info in self.uma_info_list]
            std_list = [uma_info.Std for uma_info in self.uma_info_list]

            # ax1
            self.ax.bar(name_list, mean_list, yerr=std_list, ecolor='black')

            self.ax.set_xticklabels(
                name_list, fontname='Meiryo', rotation=30, fontsize=8)

    def update_uma_info_list(self, uma_info_list: List[UmaInfo]):
        self.uma_info_list = uma_info_list
        update_func_dict = {draw_target: func for draw_target, func in zip(
            self.DrawTarget, [self.update_line, self.update_bar])}
        update_func_dict[self.draw_target]()

    def update_target(self, draw_target):
        self.draw_target = draw_target


class GraphWindow(tk.Toplevel):
    window_name = 'umauma graph'

    def __init__(self, master, graph_view: GraphView):
        super().__init__(master)
        self.geometry("500x550")
        self.title(self.window_name)
        self.graph_view = graph_view
        self._create_widgets()

    def _create_canvas(self):
        frame = ttk.Frame(self)

        # Generate canvas instance, Embedding fig in root
        self.canvas = FigureCanvasTkAgg(self.graph_view.fig, master=frame)
        self.canvas.get_tk_widget().pack()

        return frame

    def _create_buttons(self):
        frame = ttk.Frame(self)

        self.line_button = ttk.Button(frame, text="line")
        self.line_button.configure(command=self._click_draw_line)

        self.bar_button = ttk.Button(frame, text="bar")
        self.bar_button.configure(command=self._click_draw_bar)

        self.line_button.pack(side=tk.LEFT)
        self.bar_button.pack(side=tk.RIGHT)
        return frame

    def _create_widgets(self):
        self._create_canvas().pack()
        self._create_buttons().pack(pady=10, side=BOTTOM)

    def _click_draw_line(self):
        self.graph_view.update_target(GraphView.DrawTarget.LINE)
        self.graph_view.update_line()
        self.update_canvas()

    def _click_draw_bar(self):
        self.graph_view.update_target(GraphView.DrawTarget.BAR)
        self.graph_view.update_bar()
        self.update_canvas()

    def update_canvas(self):
        self.canvas.draw()
