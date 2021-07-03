import tkinter as tk
from tkinter import ttk
from typing import Dict, List, NamedTuple
from logger import init_logger

logger = init_logger(__name__)


class Content(NamedTuple):
    name: str
    rank: int
    score: int


ignore_score = -1


class ScoreTree(ttk.Treeview):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master,
                         columns=['Num', 'Rank', 'Name', 'Score'],
                         height=15, show='headings', selectmode=tk.BROWSE)

        self.tree_length = 15
        self.content_dict: Dict[str, Content] = dict()
        self.select_item: Content = None

        self._init_column()
        self._init_heading()
        self._init_data()

    def clear(self):
        for i in range(self.tree_length):
            self.set(i, 1, '')
            self.set(i, 2, '')
            self.set(i, 3, '')

            self.content_dict[str(i)] = Content(None, None, None)

    def fill(self, content_list: List[Content]):
        if len(content_list) > self.tree_length:
            logger.debug('too many content')
            logger.debug(content_list)
            logger.debug(f'len: {len(content_list)}')
            return

        sorted_list = sorted(content_list, key=self._sort_key)
        if len(sorted_list) > self.tree_length:
            sorted_list = sorted_list[:self.tree_length]

        for i, content in enumerate(sorted_list):
            self.content_dict[str(i)] = content

            if content.score and content.score == ignore_score:
                break

            raw_list = [(1, content.rank),
                        (2, content.name),
                        (3, content.score)]
            for column, value in raw_list:
                if value:
                    self.set(i, column=column, value=value)

            if self.select_item and content == self.select_item:
                self.selection_set(i)

    def _sort_key(self, content: Content):
        score = -content.score if content.score else 0
        name = content.name if content.name else ''
        return (score, name)

    def sort(self):
        content_list = [content for content in self.content_dict.values()]
        self.clear()
        self.fill(content_list)

    def fix(self, item_id: str, content: Content):
        rank = content.rank if content.rank else ''
        name = content.name if content.name else ''
        score = content.score if content.score else ''

        self.set(item_id, 1, rank)
        self.set(item_id, 2, name)
        self.set(item_id, 3, score)

        self.content_dict[item_id] = content
        self.select_item = content
        self.sort()

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
            self.content_dict[str(i)] = Content(None, None, None)
