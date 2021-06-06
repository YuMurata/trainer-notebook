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
from enum import Enum
from UmaPointReading import UmaPointReading
from matplotlib import pyplot
from Uma import UmaList
from TeamStadiumInfoDetection import TeamStadiumInfoDetection


class Win1(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.pack()

        self.master.geometry("400x400")
        self.master.title("window 1")
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

        for i, (name, point) in enumerate(self.uma_pt_list.Max().items()):
            self.treeview_score.set(i,0,name)
            self.treeview_score.set(i,1,point)

        for i, (name, point) in enumerate(self.uma_pt_list.Min().items()):
            self.treeview_score.set(i,2,point)

        for i, (name, point) in enumerate(self.uma_pt_list.Mean().items()):
            self.treeview_score.set(i,3,point)

        for i, (name, point) in enumerate(self.uma_pt_list.Std().items()):
            self.treeview_score.set(i,4,point)


    def create_widgets(self):
        # Button
        self.button_new_win2 = ttk.Button(self)
        self.button_new_win2.configure(text="Open Window 2")
        self.button_new_win2.configure(command = self.new_window2)

        self.button_new_win3 = ttk.Button(self)
        self.button_new_win3.configure(text="Open Window 3")
        self.button_new_win3.configure(command = self.new_window3)

        frame = ttk.Frame()
        frame.pack()
        #TreeView
        self.treeview_score = ttk.Treeview(frame, columns=['Name', 'Max','Min', 'Mean', 'Std'],height=30,show="headings")
        self.treeview_score.column('Name', width=120)
        self.treeview_score.column('Max', width=50)
        self.treeview_score.column('Min',anchor='e', width=50)
        self.treeview_score.column('Mean', width=50)
        self.treeview_score.column('Std', width=50)

        #Create Heading
        self.treeview_score.heading('Name', text='Name',anchor='center',command=self.click_header)
        self.treeview_score.heading('Max', text='Max',anchor='center',command=self.click_header)
        self.treeview_score.heading('Min', text='Min',anchor='center',command=self.click_header)
        self.treeview_score.heading('Mean', text='Mean',anchor='center',command=self.click_header)
        self.treeview_score.heading('Std', text='Std',anchor='center',command=self.click_header)

        self.vscroll = ttk.Scrollbar(frame, orient ="vertical", command=self.treeview_score.yview)
        self.treeview_score.configure(yscroll=self.vscroll.set)
        #Add data
        for i in range(self.uma_pt_list.len()):
            self.treeview_score.insert(parent='', index='end', iid=i ,values=(i+1, '',''))

        #self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.button_new_win2.pack()
        self.button_new_win3.pack()
        self.treeview_score.pack(side=tk.LEFT,pady=10)
        self.vscroll.pack(side=tk.RIGHT, fill="y", pady=10)

    def click_header(self):
        x = self.treeview_score.winfo_pointerx() - self.treeview_score.winfo_rootx()
        print(x)

    #Call back function
    def new_window2(self):
        self.app2 = Win2(self.master, self.uma_pt_list)

        def close_win2():
            self.app2.info_detection.stop()
            self.app2.destroy()
            self.app2 = None

        self.app2.protocol('WM_DELETE_WINDOW', close_win2)

    def new_window3(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app3 = Win3(self.newWindow)



class Win2(tk.Toplevel):
    def __init__(self,master, uma_pt_list):
        super().__init__(master)
        self.geometry("300x380")
        self.title("window 2")
        self.info_detection = TeamStadiumInfoDetection(uma_pt_list)
        self.create_widgets()
        self.info_detection.start()

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

    def deleteResultReadScore(self):
        self.read_score = []
        self.info_detection.read_score = []
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