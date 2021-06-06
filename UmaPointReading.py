import os
import pyocr
import pyocr.builders
import cv2
from PIL import Image
import sys
#import ctypes
from PIL import ImageGrab
import ctypes
from ctypes import wintypes
import numpy as np
import difflib

class UmaPointReading():

    tool = None

    def __init__(self):

        self.tool = pyocr.get_available_tools()[0]
        #self.__OpenUmaList()

    def setUmaList(self, uma_dict:dict):
        self.uma_dict = uma_dict

    # def __OpenUmaList(self):
    #     with open('uma_list.txt', 'r',encoding="utf-8_sig") as f:
    #         self.uma_list = f.read().split("\n")

    def __isint(self, s):  # 整数値を表しているかどうかを判定
        try:
            int(s)  # 文字列を実際にint関数で変換してみる
        except ValueError:
            return False
        else:
            return True

    def __ExtractUmaPt(self, line:str):
        pt = None
        uma_name = None
        tmp = line.replace(',', '').replace('.', '').replace('、', '')

        for word in tmp.split(' '):
            if 'pt' in word:
                if self.__isint(word.split('pt')[0]):
                    pt = int(word.split('pt')[0])
                else:
                    print(word)
                    return None,None
        if pt is None:
            return None, None

        name = tmp.replace(' ', '').split(str(pt))[0]
        max = 0
        for uma in self.uma_list:
            r = difflib.SequenceMatcher(None, uma, name).ratio()
            if r > max:
                uma_name = uma
                max = r
        return uma_name, pt

    def UmaPtListfromImage(self, img):
        res = self.tool.image_to_string(img,
                                    lang="jpn",
                                    builder=pyocr.builders.LineBoxBuilder(tesseract_layout=6))
        uma_pt_rank = list(range(0))
        #out = new_image
        #no = 0
        for d in res:
            #print(d.content)
            uma, pt = self.__ExtractUmaPt(d.content)
            if uma is not None:
                uma_pt_rank.append([uma, pt])
                #no = no + 1
                #print(uma + ":" + str(pt) + "pt")
            #cv2.rectangle(out, d.position[0], d.position[1], (0, 0, 255), 2)

        # cv2.imshow("img",out)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # cv2.imwrite("result.png", out)

        return uma_pt_rank