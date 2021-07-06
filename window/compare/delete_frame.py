import tkinter as tk
from tkinter import ttk
from typing import Callable, NamedTuple


class ControlFunc(NamedTuple):
    new: Callable[[], None]
    list_delete: Callable[[], None]
    status_view_delete: Callable[[], None]
    compare_view_delete: Callable[[], None]


class ControlFrame(tk.Frame):
    def __init__(self, master: tk.Widget, control_func: ControlFunc):
        super().__init__(master)

        self.new_button = ttk.Button(self, text='new')
        self.new_button.bind('<Button-1>', control_func.new)
        self.new_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.all_delete_button = ttk.Button(self, text='all_delete')
        self.all_delete_button.bind(
            '<Button-1>', self.all_delete_button_left_click)
        self.all_delete_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.all_view_delete_button = ttk.Button(self, text='all_view_clear')
        self.all_view_delete_button.bind(
            '<Button-1>', self.all_view_delete_button_left_click)
        self.all_view_delete_button.pack(
            side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.compare_view_delete_button = ttk.Button(
            self, text='compare_view_clear')
        self.compare_view_delete_button.bind(
            '<Button-1>', self.compare_view_delete_button_left_click)
        self.compare_view_delete_button.pack(
            side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.control_func = control_func

    def all_delete_button_left_click(self, event):
        self.control_func.list_delete(event)
        self.control_func.status_view_delete(event)
        self.control_func.compare_view_delete(event)

    def all_view_delete_button_left_click(self, event):
        self.control_func.status_view_delete(event)
        self.control_func.compare_view_delete(event)

    def compare_view_delete_button_left_click(self, event):
        self.control_func.compare_view_delete(event)
