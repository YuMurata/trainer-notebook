import tkinter as tk
from tkinter import ttk
from logger import init_logger
from compare_window.app import CompareApp

logger = init_logger(__name__)


def status_window_main():
    root = tk.Tk()
    root.geometry('500x500')
    ttk.Label(root, text='tabun main window').pack(
        anchor=tk.CENTER, expand=True)
    CompareApp(root)
    # 表示
    root.mainloop()


if __name__ == "__main__":
    status_window_main()
