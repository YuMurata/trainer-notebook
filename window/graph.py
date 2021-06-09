import tkinter as tk
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
        self.create_widgets()

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

    def create_widgets(self):
        # Figure instance
        fig = plt.Figure()
        self.ax = fig.add_subplot(111)
        self.ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))

        # Generate canvas instance, Embedding fig in root
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack()
