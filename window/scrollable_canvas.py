import tkinter as tk
from tkinter import ttk


class ScrollableCanvasFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, *, canvas_option: dict = None):
        super().__init__(master)
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        if canvas_option:
            self.canvas = tk.Canvas(frame, **canvas_option)
        else:
            self.canvas = tk.Canvas(frame)

        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.x_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        self.x_scroll.config(command=self.canvas.xview)
        self.x_scroll.pack(fill=tk.X, expand=True)

        self.y_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.y_scroll.config(command=self.canvas.yview)
        self.y_scroll.pack(fill=tk.Y, expand=True, anchor=tk.E)

        self.canvas.config(xscrollcommand=self.x_scroll.set,
                           yscrollcommand=self.y_scroll.set)

        self.canvas.bind("<MouseWheel>", self._scroll_y)
        self.canvas.bind("<Shift-MouseWheel>", self._scroll_x)

    def reconfig_scroll(self):
        self.canvas.update_idletasks()
        scrollregion = self.canvas.bbox("all")
        if not scrollregion:
            scrollregion = (0, 0, 0, 0)
        self.canvas.config(scrollregion=scrollregion)  # スクロール範囲

    def _scroll_y(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

    def _scroll_x(self, event):
        if event.delta > 0:
            self.canvas.xview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.xview_scroll(1, 'units')
