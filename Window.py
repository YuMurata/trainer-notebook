import os
import pyocr
import pyocr.builders
import cv2
from PIL import Image
import sys
#import ctypes
from PIL import ImageGrab, ImageEnhance
import ctypes
from ctypes import wintypes
import numpy as np
import difflib
import tkinter as tk
from tkinter import Tk, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw
from enum import IntEnum, auto
from UmaPointReading import UmaPointReading
from matplotlib import pyplot
from Uma import UmaList
from TeamStadiumInfoDetection import TeamStadiumInfoDetection


class MetricsView(ttk.Frame):
    class SortUmaPtList:
        class SortKey(IntEnum):
            NUM=1
            NAME=2
            MAX=auto()
            MIN=auto()
            MEAN=auto()
            STD=auto()

        def __init__(self):
            self.key = self.SortKey.NAME
            self.is_reverse = False
            self.key_dict = {key:value for key, value in zip(self.SortKey, MetricsView.column_name_list)}

        def sort(self, x:tuple):
            if self.key == self.SortKey.NAME:
                return x[0]
            else:
                key_list = ['max', 'min', 'mean', 'std']
                return x[1][key_list[int(self.key)-2]]

        def set_key(self, x:int):
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

    column_name_list = ['Num', 'Name', 'Max','Min', 'Mean', 'Std']

    def __init__(self, master, uma_pt_list:UmaList):
        super().__init__(master)
        self.uma_pt_sorter = self.SortUmaPtList()
        self.uma_pt_list = uma_pt_list
        self._create_widgets()
        self.display()

    def _create_heading(self):
        for metrics_name in self.column_name_list:
            metrics_text = metrics_name
            if metrics_name == self.uma_pt_sorter.key_to_str:
                if self.uma_pt_sorter.is_reverse:
                    metrics_text += ' ^'
                else:
                    metrics_text += ' v'

            self.treeview_score.heading(metrics_name, text=metrics_text, anchor='center', command=self._click_header)

    def _create_widgets(self):
        self.treeview_score = ttk.Treeview(self, columns=self.column_name_list,height=30,show="headings")
        self.treeview_score.column('Num', anchor='e',width=50)
        self.treeview_score.column('Name', anchor='w',width=120)
        self.treeview_score.column('Max', anchor='e',width=50)
        self.treeview_score.column('Min',anchor='e', width=50)
        self.treeview_score.column('Mean', anchor='e',width=50)
        self.treeview_score.column('Std', anchor='e',width=50)

        #Create Heading
        self._create_heading()

        self.vscroll = ttk.Scrollbar(self, orient ="vertical", command=self.treeview_score.yview)
        self.treeview_score.configure(yscroll=self.vscroll.set)

        #Add data
        for i in range(self.uma_pt_list.len()):
            tags = ['even'] if i % 2 == 0 else ['odd']

            self.treeview_score.insert(parent='', index='end', tags=tags, iid=i , values=[str(i+1)]+['' for _ in range(len(self.column_name_list[1:]))])

        self.treeview_score.tag_configure('odd', background='red', foreground='blue')

        #self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.treeview_score.pack(side=tk.LEFT,pady=10)
        self.vscroll.pack(side=tk.RIGHT, fill="y", pady=10)

    def _click_header(self):
        x = self.treeview_score.winfo_pointerx() - self.treeview_score.winfo_rootx()
        column = int(self.treeview_score.identify_column(x)[1])
        self.uma_pt_sorter.set_key(column)
        self.display()

    def display(self):
        #print("win1")
        # for i in range(self.uma_pt_list.len()):
        #     self.treeview_score.set(i,1,'')
        #     self.treeview_score.set(i,2,'')
        treeview_content = list(self.uma_pt_list.Metrics().items())

        treeview_content.sort(key=self.uma_pt_sorter.sort, reverse=self.uma_pt_sorter.is_reverse)
        self._create_heading()

        for i,(name, uma_data) in enumerate(treeview_content):
            self.treeview_score.set(i, 0, str(i+1))
            self.treeview_score.set(i, 1, name)
            self.treeview_score.set(i, 2, uma_data['max'])
            self.treeview_score.set(i, 3, uma_data['min'])
            self.treeview_score.set(i, 4, uma_data['mean'])
            self.treeview_score.set(i, 5, uma_data['std'])

        self.treeview_score.tag_configure('odd', background='red')

class Win1(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.pack()

        self.master.geometry("400x400")
        self.master.title("umauma drive")
        self.uma_pt_list = UmaList()
        self.create_widgets()
        self.app2 = None


    def setUmaList(self, umalist:UmaList):
        self.app2.setUmaList(umalist)

    def setResultReadScore(self, read_score:list):
        self.app2.setResultReadScore(read_score)

    def display(self):
        #print("win1")
        # for i in range(self.uma_pt_list.len()):
        #     self.treeview_score.set(i,1,'')
        #     self.treeview_score.set(i,2,'')
        self.metrics_view.display()

    def create_widgets(self):
        # Button
        self.button_new_win2 = ttk.Button(self)
        self.button_new_win2.configure(text="regist score")
        self.button_new_win2.configure(command = self.new_window2)

        self.button_new_win3 = ttk.Button(self)
        self.button_new_win3.configure(text="disp graph")
        self.button_new_win3.configure(command = self.new_window3)

        #self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.button_new_win2.pack()
        self.button_new_win3.pack()

        self.metrics_view = MetricsView(self, self.uma_pt_list)
        self.metrics_view.pack()

    #Call back function
    def new_window2(self):
        self.app2 = Win2(self.master, self.uma_pt_list, self)

        def close_win2():
            self.app2.info_detection.stop()
            self.app2.destroy()
            self.app2 = None

        self.app2.protocol('WM_DELETE_WINDOW', close_win2)

    def new_window3(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app3 = Win3(self.newWindow)



class Win2(tk.Toplevel):
    def __init__(self,master, uma_pt_list, win1):
        super().__init__(master)
        self.geometry("300x380")
        self.title("window 2")
        self.info_detection = TeamStadiumInfoDetection(uma_pt_list)
        self.create_widgets()
        self.info_detection.start()
        self.win1 = win1

    def display(self):
        read_score = self.info_detection.read_score
        #print('win2')
        #treeviewでスコアを表示する
        for i in range(15):
            self.treeview_score.set(i,1,'')
            self.treeview_score.set(i,2,'')
        for i, (name, point) in enumerate(read_score.items()):
            self.treeview_score.set(i,1,name)
            self.treeview_score.set(i,2,point)

        self.win1.display()

    def deleteResultReadScore(self):
        self.info_detection.read_score = {}
        self.display()


    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack()

        #TreeView
        self.treeview_score = ttk.Treeview(frame, columns=['Rank', 'Name','Score'],height=15,show="headings")
        self.treeview_score.column('Rank', width=40)
        self.treeview_score.column('Name', width=120)
        self.treeview_score.column('Score',anchor='e', width=50)

        #Create Heading
        self.treeview_score.heading('Rank', text='Rank',anchor='center')
        self.treeview_score.heading('Name', text='Name',anchor='center')
        self.treeview_score.heading('Score', text='Score', anchor='center')


        #Add data
        for i in range(15):
            self.treeview_score.insert(parent='', index='end', iid=i ,values=(i+1, '',''))

        self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.treeview_score.set(0,2,12345)
        # Button
        self.button_reset = ttk.Button(frame)
        self.button_reset.configure(text="削除")
        self.button_reset.configure(command=self.deleteResultReadScore)
        self.button_reset.grid(row=1,column=0)
        # Button
        self.button_register = ttk.Button(frame)
        self.button_register.configure(text="登録")
        self.button_register.configure(command=self.info_detection.OverWriteUmaListFile)
        self.button_register.grid(row=1,column=1)


class Win3(tk.Frame):
    def __init__(self,master):

        super().__init__(master)
        self.pack()
        self.master.geometry("300x300")
        self.master.title("window 3")
        self.create_widgets()

    def create_widgets(self):
        # Button
        self.button_quit = ttk.Button(self)
        self.button_quit.configure(text="Close Window 3")
        self.button_quit.configure(command=self.quit_window)
        self.button_quit.pack()

    def quit_window(self):
        self.master.destroy()

#root = tk.Tk()
#app = Win1(master=root)#Inherit
#test = []

#def loop():
#    global test
#    print("main:"+str(test))
#    app.after(1000,loop)


# def main():

#     app.after(1000,loop)
#     app.mainloop()

# if __name__ == "__main__":
#     main()