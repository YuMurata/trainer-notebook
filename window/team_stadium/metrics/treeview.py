import tkinter as tk
from tkinter import ttk
from typing import List
from uma_info import UmaInfo, UmaPointFileIO
from .sort import SortUmaInfo


class MetricsTreeView(ttk.Treeview):
    def __init__(self, master: tk.Widget):
        super().__init__(master, height=30, show="headings",
                         column=['Num'] + UmaInfo.item_name_list)

        key_list = ['Name', 'RankMean', 'Max', 'Min', 'Mean', 'Std']
        self.uma_info_sorter = SortUmaInfo(key_list)

        self._init_column()
        # Create Heading
        self._set_heading()

        self.bind('<<TreeviewSelect>>', self._click_view)

    def _init_column(self):
        column_dict = {'Num': dict(anchor=tk.E, width=50),
                       'Name': dict(anchor=tk.W, width=120),
                       'RankMean': dict(anchor=tk.E, width=80),
                       'Max': dict(anchor=tk.E, width=50),
                       'Min': dict(anchor=tk.E, width=50),
                       'Mean': dict(anchor=tk.E, width=50),
                       'Std': dict(anchor=tk.E, width=50)}

        for name, option in column_dict.items():
            self.column(name, **option)

    def _init_data(self):
        uma_info_dict = UmaPointFileIO.Read()
        content_list: List[UmaInfo] = list(uma_info_dict.values())

        content_list.sort(key=self.uma_info_sorter.sort,
                          reverse=self.uma_info_sorter.is_reverse)
        self._set_heading()

        # Add data
        for i, content in enumerate(content_list):
            num = str(i+1)
            content.scores.
            values = [str(i+1)] + \
                ['' for _ in range(len(self.column_name_list[1:]))]
            self.insert(parent='', index='end', iid=i, values=values)

    def _set_heading(self):
        for metrics_name in self.column_name_list:
            metrics_text = metrics_name
            if metrics_name == self.uma_info_sorter.sort_key:
                if self.uma_info_sorter.is_reverse:
                    metrics_text += ' ↓'
                else:
                    metrics_text += ' ↑'

            self.heading(metrics_name, text=metrics_text, anchor='center',
                         command=self._click_header)

    def _click_header(self):
        x = (self.winfo_pointerx() - self.winfo_rootx())
        column = int(self.identify_column(x)[1])
        self.uma_info_sorter.set_key(column)

        self.selection_remove(self.selection())

        if self.selected_item_dict:
            selected_item_list = list(self.selected_item_dict.values())
            self.selection_add(selected_item_list)

            sorted_items = sorted(
                self.selected_item_dict.items(), key=lambda x: x[1])
            uma_info_list = [item[0] for item in sorted_items]

            if self.graph_updater:
                self.graph_updater(uma_info_list)

        self.generate_update()

    def _click_view(self, event):
        uma_info_dict = UmaPointFileIO.Read()

        item_id_list = self.selection()

        def get_uma_info(item_id) -> UmaInfo:
            item = self.item(item_id)
            uma_name = item['values'][1]
            return uma_info_dict[uma_name]

        self.selected_item_dict = {get_uma_info(item_id): item_id
                                   for item_id in item_id_list}
        if self.graph_updater:
            self.graph_updater(list(self.selected_item_dict.keys()))
