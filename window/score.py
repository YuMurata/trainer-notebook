import tkinter as tk
from tkinter import ttk
from TeamStadiumInfoDetection import TeamStadiumInfoDetection, ScoreDispatcher
from window.app import BaseApp
from threading import Thread


class ScoreWindow(tk.Toplevel):
    def __init__(self, master, master_updater):
        super().__init__(master)
        self.title("umauma score")
        self.score_dispatcher = ScoreDispatcher(self.display)
        self.info_detection = TeamStadiumInfoDetection(self.score_dispatcher)
        self._create_widgets()
        self.info_detection.start()
        self.master_updater = master_updater

    def display(self, score: dict):
        print(f'disp: {score}')
        # print('win2')
        # treeviewでスコアを表示する
        for i in range(15):
            self.treeview_score.set(i, 1, '')
            self.treeview_score.set(i, 2, '')
        score_list = sorted(score.items(),
                            key=lambda x: x[1], reverse=True)
        for i, (name, point) in enumerate(score_list):
            self.treeview_score.set(i, 1, name)
            self.treeview_score.set(i, 2, f'{point:,}')

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
