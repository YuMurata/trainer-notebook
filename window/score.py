import tkinter as tk
from tkinter import ttk
from TeamStadiumInfoDetection import TeamStadiumInfoDetection


class ScoreWindow(tk.Toplevel):
    def __init__(self, master, win1):
        super().__init__(master)
        self.geometry("300x380")
        self.resizable(False, False)
        self.title("umauma score")
        self.info_detection = TeamStadiumInfoDetection()
        self._create_widgets()
        self.info_detection.start()
        self.win1 = win1

    def display(self):
        read_score = self.info_detection.read_score
        # print('win2')
        # treeviewでスコアを表示する
        for i in range(15):
            self.treeview_score.set(i, 1, '')
            self.treeview_score.set(i, 2, '')

        score_list = sorted(read_score.items(),
                            key=lambda x: x[1], reverse=True)
        for i, (name, point) in enumerate(score_list):
            self.treeview_score.set(i, 1, name)
            self.treeview_score.set(i, 2, f'{point:,}')

    def deleteResultReadScore(self):
        self.info_detection.read_score = {}
        self.display()

    def _create_treeview(self):
        frame = ttk.Frame(self)
        frame.pack()

        self.treeview_score = ttk.Treeview(
            frame, columns=['Rank', 'Name', 'Score'], height=15, show="headings")
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
        self.win1.display()

    def _create_widgets(self):
        self._create_treeview().pack()
        self._create_button().pack()
