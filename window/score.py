import tkinter as tk
from tkinter import ttk
from TeamStadiumInfoDetection import TeamStadiumInfoDetection, ScoreDispatcher
from window.app import BaseApp
from threading import Thread


class ScoreWindow(tk.Toplevel):
    def __init__(self, master, master_updater):
        super().__init__(master)
        self.resizable(False, False)
        self.title("umauma score")

        def generate_update_score():
            self.treeview_score.event_generate('<<UpdateScore>>', when='tail')

        def generate_update_rank():
            self.treeview_score.event_generate('<<UpdateRank>>', when='tail')
        self._create_widgets()
        self.info_detection.start()
        self.master_updater = master_updater

    def _clear_treeview(self):
        for i in range(15):
            self.treeview_score.set(i, 1, '')
            self.treeview_score.set(i, 2, '')
            self.treeview_score.set(i, 3, '')

    def _fill_treeview(self):
        def sort_key(x: Tuple[str, Dict[str, int]]):
            if 'score' in x[1]:
                return (-x[1]['score'], x[0])
            return (0, x[0])

        content_list = sorted(self.content_dict.items(), key=sort_key)
        for i, (name, content) in enumerate(content_list):
            if 'rank' in content:
                self.treeview_score.set(i, 1, content['rank'])

            if 'score' in content:
                self.treeview_score.set(i, 3, content['score'])

            self.treeview_score.set(i, 2, name)

    def update_rank(self, event):
        rank_dict = self.rank_detection.get()
        for name, rank in rank_dict.items():
            self.content_dict.setdefault(name, dict())
            self.content_dict[name]['rank'] = rank

        self._clear_treeview()
        self._fill_treeview()

    def update_score(self, event):
        logger.debug('get score')
        score_dict = self.score_detection.get()
        for name, score in score_dict.items():
            self.content_dict.setdefault(name, dict())
            self.content_dict[name]['score'] = score

        logger.debug('update content')

        with StopWatch('clear'):
            self._clear_treeview()

        with StopWatch('fill'):
            self._fill_treeview()

    def destroy(self) -> None:
        ret = super().destroy()

        def join():
            self.info_detection.stop()
            self.info_detection.join()

        Thread(daemon=True, target=join).start()
        return ret

    def deleteResultReadScore(self):
        self.score_dispatcher.init_score()

    def _create_treeview(self):
        frame = ttk.Frame(self)
        frame.pack()

        self.treeview_score = ttk.Treeview(
            frame, columns=['Rank', 'Name', 'Score'], height=15,
            show="headings")
        self.treeview_score.column('Rank', width=40)
        self.treeview_score.column('Name', width=120)
        self.treeview_score.column('Score', anchor='e', width=50)

        # Create Heading
        self.treeview_score.heading('Rank', text='Rank', anchor='center')
        self.treeview_score.heading('Name', text='Name', anchor='center')
        self.treeview_score.heading('Score', text='Score', anchor='center')

        # Add data
        for i in range(15):
            self.treeview_score.insert(
                parent='', index='end', iid=i, values=(i+1, '', ''))

        self.treeview_score.bind('<<UpdateScore>>', self.update_score)
        self.treeview_score.bind('<<UpdateRank>>', self.update_rank)
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
        self.info_detection.OverWriteUmaListFile()
        self.master_updater()

    def _create_widgets(self):
        self._create_treeview().pack()
        self._create_button().pack()


class ScoreApp(BaseApp):
    def __init__(self, master_widget: tk.Toplevel, master_updater) -> None:
        def generator():
            return ScoreWindow(master_widget, master_updater)
        target_size = (300, 380)
        super().__init__(generator, master_widget, target_size)
