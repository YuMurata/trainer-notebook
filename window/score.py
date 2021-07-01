from TeamStadiumInfoDetection.app_linked import AppLinkedThread
from typing import Callable, Dict, Tuple
import tkinter as tk
from tkinter import ttk
from TeamStadiumInfoDetection import Dispatcher
from window.app import BaseApp
from logger import init_logger

logger = init_logger(__name__)


class FixScoreFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        key_list = ['rank', 'name', 'score']
        self.entry_var_dict = {key: tk.StringVar(self) for key in key_list}
        for key in key_list:
            self._create_entry(key).pack(side=tk.LEFT)

    def _create_entry(self, key: str):
        frame = ttk.Frame(self)
        label = ttk.Label(frame, text=key)
        entry = ttk.Entry(frame, textvariable=self.entry_var_dict[key])

        label.pack()
        entry.pack()

        return frame


class ScoreWindow(tk.Toplevel):
    def __init__(self, master, metrics_updater: Callable[[], None]):
        super().__init__(master)
        # self.resizable(False, False)
        self.title("umauma score")

        def generate_update_app():
            self.treeview_score.event_generate('<<UpdateApp>>', when='tail')

        self.linked_thread = AppLinkedThread(Dispatcher(generate_update_app))
        self.linked_thread.start()

        self._create_widgets()
        self.metrics_updater = metrics_updater
        self.content_dict: Dict[str, Dict[str, int]] = dict()

    def _clear_treeview(self):
        for i in range(15):
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
        FixScoreFrame(self).pack()
        self._create_button().pack()


class ScoreApp(BaseApp):
    def __init__(self, master_widget: tk.Toplevel, master_updater) -> None:
        def generator():
            return ScoreWindow(master_widget, master_updater)
        target_size = (300, 500)
        super().__init__(generator, master_widget, target_size)
