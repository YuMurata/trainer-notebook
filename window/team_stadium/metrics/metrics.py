import tkinter as tk
from tkinter import ttk
from enum import IntEnum, auto
from Uma import UmaInfo, UmaPointFileIO
from typing import List


class SortKey(IntEnum):
    NUM = 1
    NAME = 2
    RANKMEAN = auto()
    MAX = auto()
    MIN = auto()
    MEAN = auto()
    STD = auto()


class SortUmaInfo:
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


class MetricsView(ttk.Frame):
    column_name_list = ['Num'] + UmaInfo.item_name_list
    update_view_event = '<<UpdateView>>'

    def __init__(self, master):
        super().__init__(master)
        self.uma_info_sorter = self.SortUmaInfo()
        self.selected_item_dict: dict = None
        self.graph_updater = None
        self._create_widgets()
        self.bind(self.update_view_event, self._update_view)

    def _create_heading(self):
        for metrics_name in self.column_name_list:
            metrics_text = metrics_name
            if metrics_name == self.uma_info_sorter.key_to_str:
                if self.uma_info_sorter.is_reverse:
                    metrics_text += ' ↓'
                else:
                    metrics_text += ' ↑'

            self.treeview_score.heading(
                metrics_name, text=metrics_text, anchor='center',
                command=self._click_header)

    def _create_widgets(self):
        self.treeview_score = ttk.Treeview(
            self, columns=self.column_name_list, height=30, show="headings")
        self.treeview_score.column('Num', anchor='e', width=50)
        self.treeview_score.column('Name', anchor='w', width=120)
        self.treeview_score.column('RankMean', anchor='e', width=80)
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

        self.treeview_score.selection_remove(self.treeview_score.selection())

        if self.selected_item_dict:
            selected_item_list = list(self.selected_item_dict.values())
            self.treeview_score.selection_add(selected_item_list)

            sorted_items = sorted(
                self.selected_item_dict.items(), key=lambda x: x[1])
            uma_info_list = [item[0] for item in sorted_items]

            if self.graph_updater:
                self.graph_updater(uma_info_list)

        self.generate_update()

    def _click_view(self, event):
        uma_info_dict = UmaPointFileIO.Read()

        item_id_list = self.treeview_score.selection()

        def func(item_id) -> UmaInfo:
            item = self.treeview_score.item(item_id)
            return uma_info_dict[item['values'][1]]

        self.selected_item_dict = {
            func(item_id): item_id for item_id in item_id_list}
        if self.graph_updater:
            self.graph_updater(list(self.selected_item_dict.keys()))

    def set_graph_updater(self, graph_updater):
        self.graph_updater = graph_updater

    def _update_view(self, event):
        uma_info_dict = UmaPointFileIO.Read()
        treeview_content: List[UmaInfo] = list(uma_info_dict.values())

        treeview_content.sort(key=self.uma_info_sorter.sort,
                              reverse=self.uma_info_sorter.is_reverse)
        self._create_heading()

        for i, uma_info in enumerate(treeview_content):
            if self.selected_item_dict and uma_info in self.selected_item_dict:
                self.selected_item_dict[uma_info] = i

            if i < self.score_num:
                self.treeview_score.set(i, 0, str(i+1))
                self.treeview_score.set(i, 1, uma_info.name)
                self.treeview_score.set(i, 2, f'{uma_info.RankMean:.1f}')
                self.treeview_score.set(i, 3, f'{uma_info.Max:,}')
                self.treeview_score.set(i, 4, f'{uma_info.Min:,}')
                self.treeview_score.set(i, 5, f'{uma_info.Mean:,}')
                self.treeview_score.set(i, 6, f'{uma_info.Std:,}')
            else:
                self.score_num += 1

                values = [str(i+1)] + \
                    [uma_info.name, uma_info.Max, uma_info.Min,
                        uma_info.Mean, uma_info.Std]
                self.treeview_score.insert(
                    parent='', index='end', iid=i, values=values)

        self.treeview_score.tag_configure('odd', background='red')

    def generate_update(self):
        self.event_generate(self.update_view_event, when='tail')
