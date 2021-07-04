import tkinter as tk
from tkinter import ttk
from typing import Callable, List
from uma_info import UmaInfo, UmaPointFileIO, SortUmaInfo
from logger import CustomLogger
from exception import IllegalInitializeException
logger = CustomLogger(__name__)


class MetricsTreeView(ttk.Treeview):
    update_view_event = '<<UpdateView>>'

    def __init__(self, master: tk.Widget):
        self.metrics_key_list = tuple(['Name',
                                       # 'RankMean',
                                       'Max', 'Min', 'Mean', 'Std'])
        self.column_key_list = tuple(['Num']) + self.metrics_key_list
        super().__init__(master, height=25, show="headings",
                         column=self.column_key_list)

        self.uma_info_sorter = SortUmaInfo()
        self.graph_updater = None
        self.selected_item_list: List[UmaInfo] = None

        self._init_column()
        # Create Heading
        self._set_heading()
        self._init_data()

        self.bind('<<TreeviewSelect>>', self._click_view)
        self.bind(self.update_view_event, self._update_view)

    def set_graph_updater(self,
                          graph_updater: Callable[[List[UmaInfo]], None]):
        self.graph_updater = graph_updater

    def _init_column(self):
        column_dict = {'Num': dict(anchor=tk.E, width=50),
                       'Name': dict(anchor=tk.W, width=120),
                       #    'RankMean': dict(anchor=tk.E, width=80),
                       'Max': dict(anchor=tk.E, width=50),
                       'Min': dict(anchor=tk.E, width=50),
                       'Mean': dict(anchor=tk.E, width=50),
                       'Std': dict(anchor=tk.E, width=50)}

        for name, option in column_dict.items():
            self.column(name, **option)

    def _make_content_values(self, num: int, uma_info: UmaInfo):
        scores = uma_info.scores
        return (str(num), uma_info.name, f'{scores.max:,}',
                f'{scores.min:,}', f'{scores.mean:,}', f'{scores.std:,}')

    def _init_data(self):
        uma_info_dict = UmaPointFileIO.Read()
        content_list: List[UmaInfo] = list(uma_info_dict.values())

        content_list.sort(key=self.uma_info_sorter.sort,
                          reverse=self.uma_info_sorter.is_reverse)
        self._set_heading()

        # Add data
        for i, content in enumerate(content_list):
            values = self._make_content_values(i+1, content)
            self.insert(parent='', index=i,
                        iid=content.name, values=values)

        self.content_num = len(content_list)

    def _set_heading(self):
        metrics_map = {key: sort_key
                       for key, sort_key in zip(self.metrics_key_list,
                                                self.uma_info_sorter.key_list)}

        def get_header_text(column_text: str):
            sort_key = self.uma_info_sorter.sort_key
            if metrics_map.get(column_text, 'dummy') != sort_key:
                return column_text

            sort_direction = ' ↓' if self.uma_info_sorter.is_reverse else ' ↑'
            return column_text+sort_direction

        header_text_list = tuple([get_header_text(column_key)
                                 for column_key in self.column_key_list])
        for column_name, header_text in zip(self.column_key_list,
                                            header_text_list):
            self.heading(column_name, text=header_text, anchor='center',
                         command=self._click_header)

    def _click_header(self):
        x = (self.winfo_pointerx() - self.winfo_rootx())
        column = int(self.identify_column(x)[1])
        if column <= 1:
            return
        self.uma_info_sorter.set_key_index(column-2)

        with logger.scope('click header'):
            logger.debug(f'key: {self.uma_info_sorter.sort_key}')
            logger.debug(f'is_reberse: {self.uma_info_sorter.is_reverse}')

        # if self.selected_item_dict:
        #     selected_item_list = list(self.selected_item_dict.values())
        #     # self.selection_add(selected_item_list)

        #     sorted_items = sorted(
        #         self.selected_item_dict.items(), key=lambda x: x[1])
        #     uma_info_list = [item[0] for item in sorted_items]

        #     if self.graph_updater:
        #         self.graph_updater(uma_info_list)

        self.generate_update()

    def _click_view(self, event):
        if not self.graph_updater:
            raise IllegalInitializeException('not set graph_upater')

        uma_info_dict = UmaPointFileIO.Read()

        uma_name_list = self.selection()

        # def get_uma_info(item_id) -> UmaInfo:
        #     item = self.item(item_id)
        #     uma_name = item['values'][1]
        #     return uma_info_dict[uma_name]

        self.selected_item_list = [uma_info_dict[uma_name]
                                   for uma_name in uma_name_list]
        if self.graph_updater:
            self.graph_updater(self.selected_item_list)

    def generate_update(self):
        self.event_generate(self.update_view_event)

    def _update_view(self, event):
        uma_info_dict = UmaPointFileIO.Read()
        treeview_content = uma_info_dict.to_list()

        treeview_content.sort(key=self.uma_info_sorter.sort,
                              reverse=self.uma_info_sorter.is_reverse)
        self._set_heading()

        for i, uma_info in enumerate(treeview_content):
            if self.selected_item_dict and uma_info in self.selected_item_dict:
                self.selected_item_dict[uma_info] = i

            item_id = uma_info.name
            if self.exists(item_id):
                self.move(item_id, '', i)
                self.set(item_id, 'Num', i+1)
            else:
                values = self._make_content_values(i+1, uma_info)
                self.insert(parent='', index=i, iid=item_id, values=values)
