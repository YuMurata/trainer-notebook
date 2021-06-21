import cv2
import matplotlib.pyplot as plt
from snip import ImageSnipper
from misc import pil2cv
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk


class MetricsViewStatus(ttk.Frame):
    column_name_list = ['Num', 'Status']

    def __init__(self, master):
        super().__init__(master)
        self.selected_item_dict: dict = None
        self._create_widgets()

    def _create_heading(self):
        for metrics_name in self.column_name_list:
            metrics_text = metrics_name
            self.treeview_status.heading(
                metrics_name, text=metrics_text, anchor='center')

    def _create_widgets(self):
        self.treeview_status = ttk.Treeview(
            self, columns=self.column_name_list, height=30)  # , show="headings")
        self.treeview_status.heading('#0', text='test', anchor='center')
        self.treeview_status.column('Num', anchor='e', width=50)
        self.treeview_status.column('Status', anchor='w', width=120)

        # Create Heading
        self._create_heading()

        self.vscroll = ttk.Scrollbar(
            self, orient="vertical", command=self.treeview_status.yview)
        self.treeview_status.configure(yscroll=self.vscroll.set)

        # self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.treeview_status.pack(side=tk.LEFT, pady=10)
        self.vscroll.pack(side=tk.RIGHT, fill="y", pady=10)

        # change to your file path
        self._img = tk.PhotoImage(file="resource/lose.png")
        self.treeview_status.insert('', 'end', image=self._img,
                                    value=("A's value", "B's value"))

        self._img = tk.PhotoImage(file="resource/win.png")
        self.treeview_status.insert('', 'end', text='', image=tk.PhotoImage(file="resource/win.png"),
                                    value=("A's value", "B's value"))


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


class WinStatusComparison(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.master.geometry("400x400")
        self.master.resizable(False, False)
        self.master.title("uma status")

        self.create_widgets()

    def create_widgets(self):
        # Button
        self.button_new_win2 = ttk.Button(self)
        self.button_new_win2.configure(text="regist score")
        # self.button_new_win2.configure(command=self.score_app.Activate)

        self.button_new_win3 = ttk.Button(self)
        self.button_new_win3.configure(text="disp graph")
        # self.button_new_win3.configure(command=self.graph_app.Activate)

        # self.treeview_score.grid(row=0,column=0,columnspan=2,pady=10)
        self.button_new_win2.pack()
        self.button_new_win3.pack()

        self.metrics_view = MetricsViewStatus(self)
        self.metrics_view.pack()


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
    root = tk.Tk()  # GUIのやつ

    app = WinStatusComparison(master=root)

    # 表示
    root.mainloop()


if __name__ == "__main__":
    # status_concat_main()
    status_window_main()
