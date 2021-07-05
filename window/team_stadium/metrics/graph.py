import tkinter as tk
from tkinter import ttk
from typing import List
from window.app import BaseApp
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from uma_info.uma_info import UmaInfo
from enum import Enum, auto
from colorsys import hsv_to_rgb
import mplcursors
from logger import CustomLogger
logger = CustomLogger(__name__)


class GraphView(FigureCanvasTkAgg):
    class DrawTarget(Enum):
        LINE = auto()
        BAR = auto()

    def __init__(self, master: tk.Widget):
        fig = plt.Figure()
        self.ax = fig.add_subplot(111)

        super().__init__(fig, master)

        fig.subplots_adjust(bottom=0.2, left=0.2)
        plt.rcParams['font.family'][0] = ('Meiryo')

        self.uma_info_list: List[UmaInfo] = None
        self.draw_target = self.DrawTarget.LINE
        self.update_line()

    def update_line(self):
        self.ax.cla()

        self.ax.set_xlabel('race')
        self.ax.set_ylabel('score')

        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        scatter_list = []
        if self.uma_info_list:
            h_diff = 1.0 / len(self.uma_info_list)
            for i, uma_info in enumerate(self.uma_info_list):
                x = np.arange(len(uma_info.scores))+1
                y = np.array(uma_info.scores)

                rgb = hsv_to_rgb(h_diff*i, 1, 0.8)

                # ax1
                self.ax.plot(x, y, marker='o',
                             color=rgb, label=uma_info.name)
                scatter_list.append(self.ax.scatter(x, y, marker='o',
                                                    color=rgb, label=uma_info.name))
            self.ax.legend(loc="lower right", fontsize=8,
                           prop={'family': 'Meiryo'})

        def select_line(select: mplcursors.Selection):
            name = select.artist.get_label()
            x, y = map(int, select.target)

            text = (f'{name}\n'
                    f'x={x}\n'
                    f'y={y}')
            return select.annotation.set(text=text, anncoords="offset points")
        mplcursors.cursor(scatter_list, hover=True).connect('add', select_line)
        self.draw()

    def update_bar(self):
        self.ax.cla()

        self.ax.set_xlabel('name')
        self.ax.set_ylabel('mean score')

        self.ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        if self.uma_info_list:
            name_list = [uma_info.name for uma_info in self.uma_info_list]
            mean_list = [
                uma_info.scores.mean for uma_info in self.uma_info_list]
            std_list = [uma_info.scores.std for uma_info in self.uma_info_list]

            # ax1
            self.ax.bar(name_list, mean_list, yerr=std_list, ecolor='black')

            self.ax.set_xticklabels(
                name_list, fontname='Meiryo', rotation=30, fontsize=8)

        def select_bar(select: mplcursors.Selection):
            name = name_list[select.target.index]
            mean = mean_list[select.target.index]
            text = (f'{name}\n'
                    f'mean={mean}')
            return select.annotation.set(text=text, anncoords="offset points")

        mplcursors.cursor(self.ax, hover=True).connect('add', select_bar)
        self.draw()

    def update_uma_info_list(self, uma_info_list: List[UmaInfo]):
        self.uma_info_list = uma_info_list
        update_func_dict = {draw_target: func for draw_target, func in zip(
            self.DrawTarget, [self.update_line, self.update_bar])}
        update_func_dict[self.draw_target]()

    def update_target(self, draw_target):
        self.draw_target = draw_target


class GraphFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, name='umauma graph')
        # self.graph_view = GraphView()

        # self.canvas = FigureCanvasTkAgg(self.graph_view.fig, master=self)
        self.canvas = GraphView(self)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        self._create_buttons().pack()

    def _create_buttons(self) -> ttk.Frame:
        frame = ttk.Frame(self)

        self.line_button = ttk.Button(frame, text="line")
        self.line_button.configure(command=self._click_draw_line)

        self.bar_button = ttk.Button(frame, text="bar")
        self.bar_button.configure(command=self._click_draw_bar)

        self.line_button.pack(side=tk.LEFT)
        self.bar_button.pack(side=tk.RIGHT)
        return frame

    def _click_draw_line(self):
        self.canvas.update_target(GraphView.DrawTarget.LINE)
        self.canvas.update_line()
        self.update_canvas()

    def _click_draw_bar(self):
        self.canvas.update_target(GraphView.DrawTarget.BAR)
        self.canvas.update_bar()
        self.update_canvas()

    def update_canvas(self):
        self.canvas.draw()


class GraphApp(BaseApp):
    def __init__(self, master_widget: tk.Toplevel,
                 graph_view: GraphView) -> None:
        # def generator():
        #     return GraphWindow(master_widget, graph_view)
        # target_size = (500, 550)
        # self.graph_view = graph_view
        # self.window: GraphWindow = None
        # super().__init__(generator, master_widget, target_size)
        pass

    def update_canvas(self, uma_info_list: List[UmaInfo]):
        self.graph_view.update_uma_info_list(uma_info_list)
        if self.window:
            self.window.update_canvas()
