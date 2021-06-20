import cv2
import matplotlib.pyplot as plt
from snip import ImageSnipper
from misc import pil2cv
from PIL import Image, ImageTk
import tkinter as tk


class status_comparison():

    def __init__(self) -> None:
        self.imgs = list()
        self.snipper = ImageSnipper()

    def add_status_image(self, idx=-1):
        print(len(self.imgs), idx)
        if idx != -1 and idx < len(self.imgs):
            self.imgs[idx] = self.snipper.Snip()
        else:
            self.imgs.append(self.snipper.Snip())

    def get_concat_image(self):

        width = 0
        height = self.imgs[0].height
        for img in self.imgs:
            width += img.width
        dst = Image.new('RGB', (width, height))

        paste_width = 0
        for img in self.imgs:
            dst.paste(img, (paste_width, 0))
            paste_width += img.width

        return dst


class StatusComparisonApp():
    def __init__(self) -> None:

        ### ここにイベントが発生したときの処理 ###
        self.pressed_x = self.pressed_y = 0
        item_id = -1

        root = tk.Tk()
        self.canvas = tk.Canvas(root, width=300, height=300, bg="white")
        self.canvas.pack()
        ### 図形 ###
        self.canvas.create_rectangle(
            100, 100, 120, 120, fill="red", tags="rect")
        ### 画像 ###
        self.img = Image.open("resource/lose.png")
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(200, 200, image=self.tkimg, tags="img")
        ### ここにオブジェクトとイベントを結びつける ###
        # クリックされたとき
        self.canvas.tag_bind("rect", "<ButtonPress-1>", self.pressed)
        self.canvas.tag_bind("img", "<ButtonPress-1>", self.pressed)
        # ドラッグされたとき
        self.canvas.tag_bind("rect", "<B1-Motion>", self.dragged)
        self.canvas.tag_bind("img", "<B1-Motion>", self.dragged)
        root.mainloop()

    def pressed(self, event):
        global pressed_x, pressed_y, item_id
        item_id = self.canvas.find_closest(event.x, event.y)
        tag = self.canvas.gettags(item_id[0])[0]
        item = self.canvas.type(tag)
        # print(item)
        # print(tag)
        pressed_x = event.x
        pressed_y = event.y

    def dragged(self, event):
        global pressed_x, pressed_y, item_id
        item_id = self.canvas.find_closest(event.x, event.y)
        tag = self.canvas.gettags(item_id[0])[0]
        item = self.canvas.type(tag)  # rectangle image
        delta_x = event.x - pressed_x
        delta_y = event.y - pressed_y
        if item == "rectangle":
            x0, y0, x1, y1 = self.canvas.coords(item_id)
            self.canvas.coords(item_id, x0+delta_x, y0 +
                               delta_y, x1+delta_x, y1+delta_y)
        else:
            x, y = self.canvas.coords(item_id)
            self.canvas.coords(item_id, x+delta_x, y+delta_y)
        pressed_x = event.x
        pressed_y = event.y


def status_concat_main():
    # snipper = ImageSnipper()
    sc = status_comparison()

    key = input("入力:")
    while key is not 'q':
        # snip_image = snipper.Snip()
        sc.add_status_image(int(key))
        plt.imshow(sc.get_concat_image())
        plt.show()
        key = input("入力:")


def status_window_main():
    StatusComparisonApp()


if __name__ == "__main__":
    # status_concat_main()
    status_window_main()
