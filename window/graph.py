import tkinter as tk
from tkinter import ttk
from tkinter.constants import BOTTOM
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from Uma import UmaInfo


class GraphWindow(tk.Toplevel):
    window_name = 'umauma graph'

    def __init__(self, master):
        super().__init__(master)
        self.geometry("500x500")
        self.title(self.window_name)
        self._create_widgets()

    def update_fig(self, uma_info: UmaInfo):
        x = np.arange(len(uma_info.points))+1
        y = np.array(uma_info.points)

        self.ax.cla()

        # ax1
        self.ax.plot(x, y, marker='o')
        self.ax.set_title(uma_info.name, fontname='Meiryo')
        self.ax.set_ylabel('score')
        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        self.canvas.draw()

    def _create_canvas(self):
        frame = ttk.Frame(self)
        # Figure instance
        fig = plt.Figure()
        self.ax = fig.add_subplot(111)
        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        # Generate canvas instance, Embedding fig in root
        self.canvas = FigureCanvasTkAgg(fig, master=frame)
        self.canvas.get_tk_widget().pack()

        return frame

    def _create_buttons(self):
        frame = ttk.Frame(self)

        self.line_button = ttk.Button(frame, text="line")
        self.bar_button = ttk.Button(frame, text="bar")

        self.line_button.pack(side=tk.LEFT)
        self.bar_button.pack(side=tk.RIGHT)
        self.canvas.
        return frame

    def _create_widgets(self):
        self._create_canvas().pack()
        self._create_buttons().pack(pady=10, side=BOTTOM)
