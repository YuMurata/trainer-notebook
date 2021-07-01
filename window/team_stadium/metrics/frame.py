import tkinter as tk
from tkinter import ttk
from .graph import GraphFrame
from .metrics import MetricsView


class MetricsFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        metrics = MetricsView(self)
        graph = GraphFrame(self, None)

        metrics.pack(side=tk.LEFT)
        graph.pack(side=tk.LEFT)
