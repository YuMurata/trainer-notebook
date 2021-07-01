import tkinter as tk
from tkinter import ttk


class ScoreTree(ttk.Treeview):
    def __init__(self, master: tk.Widget):
        option_dict = dict(columns=['Num', 'Rank', 'Name', 'Score'],
                           height=15, show='headings')

        super().__init__(master=master, **option_dict)
        self.tree_length = 15

    def clear(self):
        for i in range(self.tree_length):
            self.treeview_score.set(i, 1, '')
            self.treeview_score.set(i, 2, '')
            self.treeview_score.set(i, 3, '')

    def _fill_treeview(self):
        def sort_key(x: Tuple[str, Dict[str, int]]):
            logger.debug(f'name: {x[0]}, val: {x[1]}')
            if 'score' in x[1]:
                return (-x[1]['score'], x[0])
            return (0, x[0])

        logger.debug(self.content_dict)
        content_list = sorted(self.content_dict.items(), key=sort_key)
        tree_length = 15
        if len(content_list) > tree_length:
            logger.debug(content_list)
            return

        for i, (name, content) in enumerate(content_list):
            if 'rank' in content:
                self.treeview_score.set(i, 1, content['rank'])

            if 'score' in content:
                self.treeview_score.set(i, 3, content['score'])

            self.treeview_score.set(i, 2, name)

    def update_app(self, event):
        self.content_dict = self.linked_thread.get()

        self._clear_treeview()
        self._fill_treeview()

    def destroy(self) -> None:
        self.linked_thread.stop()
        return super().destroy()

    def deleteResultReadScore(self):
        self.linked_thread.init_dict()
        self.treeview_score.event_generate('<<UpdateApp>>', when='tail')

    def _create_treeview(self):
        frame = ttk.Frame(self)
        frame.pack()

        self.treeview_score = ttk.Treeview(
            frame, columns=['Num', 'Rank', 'Name', 'Score'], height=15,
            show="headings")
        self.treeview_score.column('Num', width=40)
        self.treeview_score.column('Rank', width=40)
        self.treeview_score.column('Name', width=120)
        self.treeview_score.column('Score', anchor='e', width=50)

        # Create Heading
        self.treeview_score.heading('Num', text='Num', anchor='center')
        self.treeview_score.heading('Rank', text='Rank', anchor='center')
        self.treeview_score.heading('Name', text='Name', anchor='center')
        self.treeview_score.heading('Score', text='Score', anchor='center')

        # Add data
        for i in range(15):
            self.treeview_score.insert(
                parent='', index='end', iid=i, values=(i+1, '', ''))

        self.treeview_score.bind('<<UpdateApp>>', self.update_app)
        self.treeview_score.pack()

        return frame

    def _create_button(self):
        frame = ttk.Frame(self)
        frame.pack()

        self.button_reset = ttk.Button(frame)
        self.button_reset.configure(text="削除")
        self.button_reset.configure(command=self.deleteResultReadScore)
        self.button_reset.pack(side=tk.LEFT)

        # Button
        self.button_register = ttk.Button(frame)
        self.button_register.configure(text="登録")
        self.button_register.configure(
            command=self._regist)
        self.button_register.pack(side=tk.RIGHT)

        return frame

    def _regist(self):
        self.linked_thread.overwrite_umainfo_file()
        self.metrics_updater()

    def _create_widgets(self):
        self._create_treeview().pack()
        FixScoreFrame(self).pack(expand=True, fill=tk.BOTH)
        self._create_button().pack()
