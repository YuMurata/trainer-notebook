import tkinter as tk
from tkinter import ttk
from enum import IntEnum, auto
from window import ScoreWindow, GraphWindow
from Uma import UmaInfo, UmaPointFileIO
from typing import List


class MetricsView(ttk.Frame):
    column_name_list = ['Num'] + UmaInfo.item_name_list

    class SortUmaInfo:
        class SortKey(IntEnum):
            NUM = 1
            NAME = 2
            MAX = auto()
            MIN = auto()
            MEAN = auto()
            STD = auto()

        def __init__(self):
            self.key = self.SortKey.NAME
            self.is_reverse = False
            self.key_dict = {key: value for key, value in zip(
                self.SortKey, MetricsView.column_name_list)}

        def sort(self, uma_info: UmaInfo):
            return uma_info[UmaInfo.item_name_list[int(self.key)-2]]

        def set_key(self, x: int):
            key = self.SortKey(x)
            if key == self.SortKey.NUM:
                return

            if key == self.key:
                self.is_reverse = not self.is_reverse
            else:
                self.is_reverse = False

            self.key = key

        @property
        def key_to_str(self):
            return self.key_dict[self.key]

    def __init__(self, master):
        super().__init__(master)
        self.uma_info_sorter = self.SortUmaInfo()
        self.graph_updater = None
        self._create_widgets()

    def _create_heading(self):
        for metrics_name in self.column_name_list:
            metrics_text = metrics_name
            if metrics_name == self.uma_info_sorter.key_to_str:
                if self.uma_info_sorter.is_reverse:
                    metrics_text += ' ^'
                else:
                    metrics_text += ' v'

            self.treeview_score.heading(
                metrics_name, text=metrics_text, anchor='center',
                command=self._click_header)

    def _create_widgets(self):
        self.treeview_score = ttk.Treeview(
            self, columns=self.column_name_list, height=30, show="headings")
        self.treeview_score.column('Num', anchor='e', width=50)
        self.treeview_score.column('Name', anchor='w', width=120)
        self.treeview_score.column('Max', anchor='e', width=50)
        self.treeview_score.column('Min', anchor='e', width=50)
        self.treeview_score.column('Mean', anchor='e', width=50)
        self.treeview_score.column('Std', anchor='e', width=50)

        # Create Heading
        self._create_heading()

        self.vscroll = ttk.Scrollbar(
            self, orient="vertical", command=self.treeview_score.yview)
        self.treeview_score.configure(yscroll=self.vscroll.set)

        self.score_num = len(UmaPointFileIO.Read())
        # Add data
        for i in range(self.score_num):
            tags = ['even'] if i % 2 == 0 else ['odd']

            values = [str(i+1)] + \
                ['' for _ in range(len(self.column_name_list[1:]))]
            self.treeview_score.insert(parent='', index='end', tags=tags,
                                       iid=i, values=values)

        self.treeview_score.tag_configure(
            'odd', background='red', foreground='blue')

        # self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.treeview_score.pack(side=tk.LEFT, pady=10)
        self.vscroll.pack(side=tk.RIGHT, fill="y", pady=10)

        self.treeview_score.bind('<<TreeviewSelect>>', self._click_view)

    def _click_header(self):
        x = (self.treeview_score.winfo_pointerx() -
             self.treeview_score.winfo_rootx())
        column = int(self.treeview_score.identify_column(x)[1])
        self.uma_info_sorter.set_key(column)
        self.display()

    def _click_view(self, event):
        item_id = self.treeview_score.selection()[0]
        item = self.treeview_score.item(item_id)
        uma_info_dict = UmaPointFileIO.Read()
        uma_info = uma_info_dict[item['values'][1]]

        if self.graph_updater:
            self.graph_updater(uma_info)

    def set_graph_updater(self, graph_updater):
        self.graph_updater = graph_updater

    def display(self):
        uma_info_dict = UmaPointFileIO.Read()
        treeview_content: List[UmaInfo] = list(uma_info_dict.values())

        treeview_content.sort(key=self.uma_info_sorter.sort,
                              reverse=self.uma_info_sorter.is_reverse)
        self._create_heading()

        for i, uma_info in enumerate(treeview_content):
            if i < self.score_num:
                self.treeview_score.set(i, 0, str(i+1))
                self.treeview_score.set(i, 1, uma_info.name)
                self.treeview_score.set(i, 2, uma_info.Max)
                self.treeview_score.set(i, 3, uma_info.Min)
                self.treeview_score.set(i, 4, uma_info.Mean)
                self.treeview_score.set(i, 5, uma_info.Std)
            else:
                self.score_num += 1

                values = [str(i+1)] + \
                    [uma_info.name, uma_info.Max, uma_info.Min,
                        uma_info.Mean, uma_info.Std]
                self.treeview_score.insert(
                    parent='', index='end', iid=i, values=values)

        self.treeview_score.tag_configure('odd', background='red')


class Win1(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.master.geometry("400x400")
        self.master.title("umauma drive")
        self.create_widgets()
        self.app2 = None
        self.app3 = None
        self.display()
        self.master.protocol('WM_DELETE_WINDOW', self._close_win1)

    def display(self):
        self.metrics_view.display()

    def create_widgets(self):
        # Button
        self.button_new_win2 = ttk.Button(self)
        self.button_new_win2.configure(text="regist score")
        self.button_new_win2.configure(command=self.new_window2)

        self.button_new_win3 = ttk.Button(self)
        self.button_new_win3.configure(text="disp graph")
        self.button_new_win3.configure(command=self.new_window3)

        # self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.button_new_win2.pack()
        self.button_new_win3.pack()

        self.metrics_view = MetricsView(self)
        self.metrics_view.pack()

    def _close_win1(self):
        if self.app2:
            self.app2.info_detection.stop()
            self.app2.info_detection.join()
            self.app2.destroy()
            self.app2 = None
        self.master.destroy()

    # Call back function
    def new_window2(self):
        self.score_app = ScoreWindow(self.master, self)

        def close_win2():
            self.score_app.info_detection.stop()
            self.score_app.destroy()
            self.score_app = None

            self.app2.protocol('WM_DELETE_WINDOW', close_win2)

    def new_window3(self):
        self.graph_app = GraphWindow(self.master)
        self.metrics_view.set_graph_updater(self.graph_app.update_fig)
