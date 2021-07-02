import tkinter as tk
from tkinter import ttk
from typing import List, NamedTuple
from logger import init_logger

logger = init_logger(__name__)


class Content(NamedTuple):
    name: str
    rank: int
    score: int


class ScoreTree(ttk.Treeview):
    def __init__(self, master: tk.Widget):
        option_dict = dict(columns=['Num', 'Rank', 'Name', 'Score'],
                           height=15, show='headings')

        super().__init__(master=master, **option_dict)

        self.tree_length = 15

        self._init_column()
        self._init_heading()
        self._init_data()

    def clear(self):
        for i in range(self.tree_length):
            self.treeview_score.set(i, 1, '')
            self.treeview_score.set(i, 2, '')
            self.treeview_score.set(i, 3, '')

    def fill(self, content_list: List[Content]):
        if len(content_list) > self.tree_length:
            logger.debug(content_list)
            return

        for i, content in enumerate(content_list):
            raw_list = [(1, content.rank), (2, content.name),
                        (3, content.score)]
            for column, value in raw_list:
                if value:
                    self.set(i, column=column, value=value)

    def fix(self, item_id: str, content: Content):
        rank = content.rank if content.rank else ''
        name = content.name if content.name else ''
        score = content.score if content.score else ''

        self.set(item_id, 1, rank)
        self.set(item_id, 2, name)
        self.set(item_id, 3, score)
    def _init_column(self):
        self.column('Num', width=40)
        self.column('Rank', width=40)
        self.column('Name', width=120)
        self.column('Score', anchor='e', width=50)

    def _init_heading(self):
        self.heading('Num', text='Num', anchor='center')
        self.heading('Rank', text='Rank', anchor='center')
        self.heading('Name', text='Name', anchor='center')
        self.heading('Score', text='Score', anchor='center')

    def _init_data(self):
        for i in range(self.tree_length):
            num = str(i+1)
            rank = ''
            name = ''
            score = ''
            value = (num, rank, name, score)

            self.insert(parent='', index='end', iid=i, values=value)
