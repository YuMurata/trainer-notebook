import tkinter as tk
from tkinter import ttk
from logger import init_logger
from compare_window.app import CompareApp

logger = init_logger(__name__)


def status_window_main():
    CompareApp(None).mainloop()
    # 表示


if __name__ == "__main__":
    status_window_main()
