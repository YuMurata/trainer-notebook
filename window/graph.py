import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class GraphWindow(tk.Toplevel):
    window_name = 'umauma graph'
    def __init__(self,master):
        super().__init__(master)
        self.geometry("500x500")
        self.title(self.window_name)
        self.create_widgets()

    def test(self):
        x1 = np.linspace(0.0, 5.0)
        y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
        x2 = np.linspace(0.0, 3.0)
        y2 = np.cos(2 * np.pi * x2) * np.exp(-x1)

        # Figure instance
        fig = plt.Figure()

        # ax1
        ax1 = fig.add_subplot(221)
        ax1.plot(x1, y1)
        ax1.set_title('line plot')
        ax1.set_ylabel('Damped oscillation')

        # ax2
        ax2 = fig.add_subplot(222)
        ax2.scatter(x1, y1, marker='o')
        ax2.set_title('Scatter plot')

        # ax3
        ax3 = fig.add_subplot(223)
        ax3.plot(x2, y2)
        ax3.set_ylabel('Damped oscillation')
        ax3.set_xlabel('time (s)')

        # ax4
        ax4 = fig.add_subplot(224)
        ax4.scatter(x2, y2, marker='o')
        ax4.set_xlabel('time (s)')

        return fig

    def create_widgets(self):
        fig = self.test()

        self.canvas = FigureCanvasTkAgg(fig, master=self)  # Generate canvas instance, Embedding fig in root
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
