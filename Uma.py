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
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw
from enum import Enum
from UmaPointReading import UmaPointReading
from matplotlib import pyplot
import statistics

class UmaList():
    def __init__(self):
        self.readUmaList()
        self.WriteUmaList()
        pass

    def readUmaList(self):
        self.uma_pt_dict = {}
        with open('uma_pt_list.txt', 'r',encoding="utf-8_sig") as f:
            max_data = 0
            for line in f.readlines():
                line = line.replace("\n", "").replace(' ','').replace('　','')
                if line == '':
                    continue
                #uma_pt = []
                word_list = line.split(",")
                uma_name = word_list[0]
                points = []
                if len(word_list) > 1:
                    points = map(int, word_list[1:])

                self.uma_pt_dict[uma_name] = points

                if max_data < len(points):
                    max_data = len(points)

        for name in self.uma_pt_dict.keys():
            self.uma_pt_dict[name] += [0 for j in range(max-len(self.uma_pt_dict[name]))]

    def WriteUmaList(self):
        with open('uma_pt_list.txt', 'w', encoding="utf-8_sig") as f:
            for name, points in self.uma_pt_dict.items():
                f.write(name)
                for data in points:
                    f.write(', ' + str(data))
                f.write('\n')

    def getUmaList(self):
        return sorted(self.uma_pt_dict.keys())

    def addUmaPt(self, read_score:dict):
        for name, points in self.uma_pt_dict.keys():
            if name in sorted(read_score.keys()):
                uma_pt_dict[name].insert(0, read_score[name])
            else:
                self.uma_pt_dict[name].insert(0,0)

    def Max(self):
        pass

if __name__ == "__main__":
    uma_list = UmaList()
    print(uma_list.getUmaList())