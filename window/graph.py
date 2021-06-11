import tkinter as tk
from tkinter import ttk
from tkinter.constants import BOTTOM
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from Uma import UmaInfo, UmaPointFileIO
from enum import Enum, auto


class GraphWindow(tk.Toplevel):
    window_name = 'umauma graph'

    class DrawTarget(Enum):
        LINE = auto()
        BAR = auto()

    def __init__(self, master):
        super().__init__(master)
        self.geometry("500x550")
        self.title(self.window_name)
        self._create_widgets()
        self.draw_target = self.DrawTarget.LINE

    def update_fig(self, uma_info: UmaInfo):
        if self.draw_target == self.DrawTarget.LINE:
            x = np.arange(len(uma_info.points))+1
            y = np.array(uma_info.points)

            self.ax.cla()

            # ax1
            self.ax.plot(x, y, marker='o')
            self.ax.set_title(uma_info.name, fontname='Meiryo')
            self.ax.set_ylabel('score')
            self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
            self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))

            self.canvas.draw()

    def _create_canvas(self):
        frame = ttk.Frame(self)
        # Figure instance
        fig = plt.Figure()
        self.ax = fig.add_subplot(111)
        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        # Generate canvas instance, Embedding fig in root
        self.canvas = FigureCanvasTkAgg(fig, master=frame)
        self.canvas.get_tk_widget().pack()

        fig.subplots_adjust(bottom=0.2)

        return frame

    def _create_buttons(self):
        frame = ttk.Frame(self)

        self.line_button = ttk.Button(frame, text="line")
        self.line_button.configure(command=self._click_draw_line)

        self.bar_button = ttk.Button(frame, text="bar")
        self.bar_button.configure(command=self._draw_bar)

        self.line_button.pack(side=tk.LEFT)
        self.bar_button.pack(side=tk.RIGHT)
        return frame

    def _create_widgets(self):
        self._create_canvas().pack()
        self._create_buttons().pack(pady=10, side=BOTTOM)

    def _click_draw_line(self):
        self.draw_target = self.DrawTarget.LINE
        self.ax.cla()
        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
        self.canvas.draw()

    def _draw_bar(self):
        self.draw_target = self.DrawTarget.BAR
        uma_info_list = list(UmaPointFileIO.Read().values())

        self.ax.cla()

        name_list = [uma_info.name for uma_info in uma_info_list]
        mean_list = [uma_info.Mean for uma_info in uma_info_list]
        std_list = [uma_info.Std for uma_info in uma_info_list]

        # ax1
        self.ax.bar(name_list, mean_list, yerr=std_list, ecolor='black')

        self.ax.set_xticklabels(
            name_list, fontname='Meiryo', rotation=30, fontsize=8)
        self.ax.set_ylabel('mean score')
        self.canvas.draw()
