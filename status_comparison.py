from typing import Callable,  Dict, NamedTuple
import cv2
import matplotlib.pyplot as plt
from snip import ImageSnipper
from misc import cv2pil, pil2cv
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import PhotoImage, ttk
from logger import init_logger

logger = init_logger(__name__)


class ButtonFunc(NamedTuple):
    status: Callable[[Image.Image], None]
    add: Callable[[], None]
    delete: Callable[[int], None]


class UmaFrame(tk.Frame):

    def __init__(self, master: tk.Widget, snipper: ImageSnipper,
                 button_func: ButtonFunc):
        super().__init__(master)

        status_frame = tk.Frame(self)
        status_frame.pack(side=tk.LEFT, pady=5, fill=tk.Y)
        self.status_button = ttk.Button(status_frame, text='status')
        self.status_button.bind('<Button-1>', self.status_button_left_click)
        self.status_button.pack(expand=True, fill=tk.Y)

        controll_frame = tk.Frame(self)
        controll_frame.pack(side=tk.RIGHT, pady=5)

        add_button = ttk.Button(controll_frame, text='add')
        add_button.bind('<Button-1>', self.add_button_left_click)
        add_button.bind('<Button-3>', self.add_button_right_click)
        delete_button = ttk.Button(controll_frame, text='delete')
        delete_button.bind('<Button-1>', self.delete_button_left_click)

        add_button.pack(fill=tk.X)
        delete_button.pack(fill=tk.X)

        self.snipper = snipper
        self.image: Image.Image = None

        self.status_rect = (0, 53, self.snipper.snip_size.width, 623)

        self.add_flag = False
        self.button_func = button_func

        self.item_id: int = None

    def set_item_id(self, item_id: int):
        self.item_id = item_id

    def status_button_left_click(self, event):
        # 選択した表示エリアにステータスの画像を表示して
        if self.image:
            self.button_func.status(self.image)

    def add_button_left_click(self, event):
        # 画像を取得して
        self.image = self.snipper.Snip()
        self.image = self.image.crop(self.status_rect)
        self.set_status_button_image()
        if not self.add_flag:
            self.button_func.add()
            self.add_flag = True

        logger.debug(f'add size: {self.winfo_height()}')

    def add_button_right_click(self, event):
        # 画像を取得・結合して
        if not self.add_flag:
            self.button_func.add()
            self.add_flag = True

        if not self.image:
            self.image = self.snipper.Snip()
            self.image = self.image.crop(self.status_rect)
            self.set_status_button_image()

        else:
            w = self.snipper.snip_size.width
            snip_img2 = self.snipper.Snip()
            snip_img2 = snip_img2.crop(self.status_rect)
            # 592,622
            template = self.image.crop(
                (0, self.image.height - 31, self.image.width,
                 self.image.height - 1))

            res = cv2.matchTemplate(pil2cv(snip_img2), pil2cv(
                template), cv2.TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            top_left = min_loc
            bottom_right = (top_left[0] + template.width,
                            top_left[1]+template.height)

            result = pil2cv(snip_img2)
            cv2.rectangle(result, top_left, bottom_right, 255, 2)

            dst = Image.new('RGB', (w, self.image.height - 31 +
                            snip_img2.height - top_left[1]))
            dst.paste(self.image, (0, 0))
            dst.paste(snip_img2.crop((
                0, top_left[1], w, snip_img2.height)),
                (0, self.image.height - 31))

            plt.subplot(221).imshow(self.image)
            plt.subplot(222).imshow(snip_img2)
            plt.subplot(223).imshow(cv2pil(result))
            plt.subplot(224).imshow(dst)
            plt.show()
            self.image = dst

    def delete_button_left_click(self, event):
        # 消して
        self.button_func.delete(self.item_id)

    def set_status_button_image(self):

        status_img = self.image.crop(
            (0, 117, self.snipper.snip_size.width, 167))

        uma_img = self.image.crop((40, 20, 120, 100))
        uma_img = uma_img.resize((int(uma_img.width/uma_img.height *
                                      status_img.height), status_img.height))

        concat_img = Image.new(
            'RGB', (uma_img.width + status_img.width, status_img.height))
        concat_img.paste(uma_img, (0, 0))
        concat_img.paste(status_img, (uma_img.width, 0))
        concat_img = concat_img.resize(
            (int(concat_img.width/1.5), int(concat_img.height/1.5)))

        self.bt_img = ImageTk.PhotoImage(image=concat_img)
        self.status_button.configure(image=self.bt_img)


class ListFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, snipper: ImageSnipper,
                 show_image: Callable[[Image.Image], None]):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=500, bg='white')
        self.snipper = snipper
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.config(command=self.canvas.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.scroll.set)
        self.set_mousewheel(self.canvas, self._scroll_y)

        self.umaframe_dict: Dict[int, UmaFrame] = dict()
        self.show_image = show_image
        self.add_umaframe()

    def set_mousewheel(self, widget, command):
        """Active / deactivate mousewheel scrolling when
        cursor is over / not over the widget respectively."""
        widget.bind("<Enter>", lambda e: widget.bind_all(
            '<MouseWheel>', lambda e: command(e)))
        widget.bind("<Leave>", lambda e: widget.unbind_all('<MouseWheel>'))

    def _get_frame_xy(self, frame_idx: int):
        x = 0
        umaframe_height = 60
        y = frame_idx*(umaframe_height+10)

        return x, y

    def add_umaframe(self):
        button_func = ButtonFunc(
            self.show_image, self.add_umaframe, self.delete_umaframe)
        umaframe = UmaFrame(self.canvas, self.snipper,
                            button_func)

        item_id = self.canvas.create_window(
            self._get_frame_xy(len(self.umaframe_dict)), window=umaframe,
            anchor='nw')
        umaframe.set_item_id(item_id)

        self._reconfig_scroll()
        self.umaframe_dict[item_id] = umaframe

    def _reconfig_scroll(self):
        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲
        logger.debug(self.canvas.bbox("all"))

    def delete_umaframe(self, delete_id: int):
        if len(self.umaframe_dict) <= 1:
            return
        if not self.umaframe_dict[delete_id].image:
            return

        self.umaframe_dict.pop(delete_id)
        self.canvas.delete(delete_id)

        for i, item_id in enumerate(self.umaframe_dict.keys()):
            self.canvas.moveto(item_id, *self._get_frame_xy(i))

        self._reconfig_scroll()

    def all_delete_umaframe(self, event):
        item_list = list(self.umaframe_dict.items())
        for item_id, umaframe in item_list:
            if len(self.umaframe_dict) == 1:
                break

            if umaframe.image:
                self.umaframe_dict.pop(item_id)
                self.canvas.delete(item_id)

        for i, item_id in enumerate(self.umaframe_dict.keys()):
            self.canvas.moveto(item_id, *self._get_frame_xy(i))

        self._reconfig_scroll()

    def _scroll_y(self, event):
        if self.canvas.bbox("all")[3] < self.canvas.winfo_height():
            return
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')


class SelectFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, snipper: ImageSnipper,
                 show_image: Callable[[Image.Image], None]):
        super().__init__(master)

        self.list_frame = ListFrame(self, snipper, show_image)
        self.list_frame.pack(fill=tk.Y, expand=True)

        all_delete_button = ttk.Button(self, text='all_delete')
        all_delete_button.pack()
        all_delete_button.bind(
            '<Button-1>', self.list_frame.all_delete_umaframe)


class StatusFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=400, height=500)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.photoimage: ImageTk.PhotoImage = None
        self.image_id: int = None

        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.config(command=self.canvas.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.scroll.set)
        self.canvas.bind("<MouseWheel>", self._scroll_y)

    def select_image(self, image: Image.Image):
        self.photoimage = ImageTk.PhotoImage(image=image)

        if not self.image_id:
            self.canvas.create_image(
                0, 0, anchor='nw', image=self.photoimage)
        else:
            self.canvas.itemconfig(self.image_id, image=self.photoimage)

        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"))  # スクロール範囲

    def _scroll_y(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')


class CompareFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master, relief='ridge')
        self.canvas = tk.Canvas(self)
        self.canvas.pack()
        self.scroll = ttk.Scrollbar(self, orient='horizontal')
        self.scroll.pack()

    def add_image(self, image: Image.Image):
        self.photoimage = ImageTk.PhotoImage(image=image)


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
        self.buttons = []
        self.but_img = []
        self.img = []
        self.pack()

        self.master.title("Status Comparison")
        self.snipper = ImageSnipper()

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self, bg='white', bd=2)
        self.main_frame.pack(fill=tk.BOTH)

        self.create_left_frame()
        self.create_status_frame1()

        self.status_frame2 = tk.Frame(self.main_frame, bg='green', bd=2)
        self.status_frame2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        pass

    def create_left_frame(self):
        self.left_frame = tk.Frame(self.main_frame, bg='blue', bd=2)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.list_frame = tk.Frame(self.left_frame,
                                   bg='green', bd=2)
        self.list_frame.pack(fill=tk.BOTH)
        # Canvas Widget を生成
        self.list_canvas = tk.Canvas(self.list_frame, width=500)

        # Scrollbar を生成して配置
        self.bar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bar.config(command=self.list_canvas.yview)

        # Canvas Widget を配置
        self.list_canvas.config(yscrollcommand=self.bar.set)

        self.list_canvas.pack(side=tk.LEFT)
        self.list_frame.pack()
        # but = tk.Button(left_frame, text='追加！！！！！')
        # but.pack(side=tk.LEFT, fill=tk.X, expand=True)

        but = tk.Button(self.left_frame, text='全削除！！！！！')
        but.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Frame Widgetを 生成
        self.btn_frame = tk.Frame(self.list_canvas)

        # Frame Widgetを Canvas Widget上に配置
        self.list_canvas.create_window((0, 0), window=self.btn_frame, anchor=tk.NW,
                                       width=self.list_canvas.cget('width'))

        # 複数の Button Widget 生成し、Frame上に配置
        # buttons = []
        self.img.append(tk.PhotoImage(file='./resource/lose.png'))
        bt = tk.Button(self.btn_frame, text='追加')
        bt.bind("<1>", self.btn_left_click(len(self.buttons)))
        bt.bind("<3>", self.btn_right_click(len(self.buttons)))
        bt.bind("<Double-1>", self.btn_double_click(len(self.buttons)))
        self.buttons.append(bt)
        bt.pack(fill=tk.X, expand=True)

        self.list_canvas.update_idletasks()
        self.list_canvas.config(
            scrollregion=self.list_canvas.bbox("all"))  # スクロール範囲
        print(self.list_canvas.bbox("all"))

    def create_status_frame1(self):
        self.status_frame1 = tk.Frame(
            self.main_frame, width=200, bg='red', bd=2)
        self.status_frame1.pack(side=tk.LEFT, fill=tk.Y)

        # img2 = tk.PhotoImage(file='./resource/win.png')
        # img2 = tk.PhotoImage(image=self.snipper.Snip())
        self.img2 = ImageTk.PhotoImage(image=self.snipper.Snip())
        canvas_status1 = tk.Canvas(self.status_frame1, width=self.img2.width())
        canvas_status1.create_image(0, 0, image=self.img2, anchor=tk.NW)
        canvas_status1.pack(expand=True, fill=tk.BOTH)
        self.img.append(tk.PhotoImage(file='./resource/win.png'))
        self.img.append(tk.PhotoImage(self.snipper.Snip()))

    def add_uma_frame(self):
        self.uma_frame.append(tk.Frame(self.main_frame, bg='blue', bd=2))
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

    def btn_left_click(self, i):
        def x(event):
            print("left", i)
            # self.but_img.append(tk.PhotoImage(file='./resource/win.png'))
            # self.but_img.append(tk.PhotoImage(self.snipper.Snip()))

            img = self.snipper.Snip()
            self.img.append(img)
            self.temp = ImageTk.PhotoImage(
                image=img.crop((0, 170, img.width, 230)))

            # self.buttons[i].configure(image=self.img[1])

            # buttons[i].configure(text='aaa')
            if i == len(self.buttons) - 1:
                self.but_img.append(self.temp)
                bt = tk.Button(self.btn_frame, text='追加')
                bt.bind("<1>", self.btn_left_click(len(self.buttons)))
                self.buttons.append(bt)
                bt.pack(fill=tk.X)
                self.list_canvas.update_idletasks()
                self.list_canvas.config(
                    scrollregion=self.list_canvas.bbox("all"))  # スクロール範囲
            else:
                self.but_img[i] = self.temp

            self.buttons[i].configure(image=self.but_img[i])
        return x

    def btn_right_click(self, i):
        def x(event):
            print("right", i)
        return x

    def btn_double_click(self, i):
        def x(event):
            print("double", i)
        return x

    def status_image_combine(self, img1, img2):

        template = img1.crop(
            (0, img1.height - 31, img1.width, img1.height - 1))

        res = cv2.matchTemplate(pil2cv(img2), pil2cv(
            template), cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        top_left = min_loc
        bottom_right = (top_left[0] + template.width,
                        top_left[1]+template.height)

        result = pil2cv(img2)
        cv2.rectangle(result, top_left, bottom_right, 255, 2)

        dst = Image.new('RGB', (img1.width, img1.height - 31 +
                                img2.height - top_left[1]))
        dst.paste(img1, (0, 0))
        dst.paste(img2.crop((
            0, top_left[1], img1.width, img2.height)), (0, img1.height - 31))
        return dst
# buttons = []
# img_win = []


# def canvas_scroll_main():
#     global buttons
#     global img_win

#     root = tk.Tk()
#     root.title("Status Comparison")
#     # root.geometry("1000x1000")
#     main_frame = tk.Frame(root, bg='white', bd=2)
#     main_frame.pack(fill=tk.BOTH)
#     left_frame = tk.Frame(main_frame, bg='blue', bd=2)
#     left_frame.pack(side=tk.LEFT, fill=tk.Y)

#     status_frame1 = tk.Frame(main_frame, width=200, bg='red', bd=2)
#     status_frame1.pack(side=tk.LEFT, fill=tk.Y)

#     status_frame2 = tk.Frame(main_frame, bg='green', bd=2)
#     status_frame2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

#     list_frame = tk.Frame(left_frame,
#                           bg='green', bd=2)
#     list_frame.pack(fill=tk.BOTH)
#     # Canvas Widget を生成
#     list_canvas = tk.Canvas(list_frame, width=200)

#     # Scrollbar を生成して配置
#     bar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
#     bar.pack(side=tk.RIGHT, fill=tk.Y)
#     bar.config(command=list_canvas.yview)

#     # Canvas Widget を配置
#     list_canvas.config(yscrollcommand=bar.set)

#     list_canvas.pack(side=tk.LEFT)
#     list_frame.pack()
#     # but = tk.Button(left_frame, text='追加！！！！！')
#     # but.pack(side=tk.LEFT, fill=tk.X, expand=True)
#     but = tk.Button(left_frame, text='全削除！！！！！')
#     but.pack(side=tk.RIGHT, fill=tk.X, expand=True)

#     # Frame Widgetを 生成
#     btn_frame = tk.Frame(list_canvas)

#     # Frame Widgetを Canvas Widget上に配置
#     list_canvas.create_window((0, 0), window=btn_frame, anchor=tk.NW,
#                               width=list_canvas.cget('width'))

#     # 複数の Button Widget 生成し、Frame上に配置
#     # buttons = []
#     canvas_height = 0
#     img = tk.PhotoImage(file='./resource/lose.png')
#     for i in range(20):
#         bt = tk.Button(btn_frame, image=img)
#         bt.bind("<1>", btn_click(i))
#         buttons.append(bt)
#         bt.pack(fill=tk.X)
#         canvas_height += bt.winfo_reqheight()
#     list_canvas.update_idletasks()
#     list_canvas.config(scrollregion=list_canvas.bbox("all"))  # スクロール範囲
#     print(list_canvas.bbox("all"))

#     img2 = tk.PhotoImage(file='./resource/win.png')
#     canvas_status1 = tk.Canvas(status_frame1, width=img2.width())
#     canvas_status1.create_image(0, 0, image=img2, anchor=tk.NW)
#     canvas_status1.pack(expand=True, fill=tk.BOTH)
#     img_win = tk.PhotoImage(file='./resource/win.png')
#     root.mainloop()


# def btn_click(i):

#     def x(event):
#         print(i)
#         global buttons
#         global img_win

#         snipper = ImageSnipper()
#         snip_img = tk.PhotoImage(snipper.Snip())
#         buttons[i].configure(image=img_win)
#         # buttons[i].configure(text='aaa')
#     return x


def status_window_main():
    root = tk.Tk()  # GUIのやつ

    snipper = ImageSnipper()

    # app = WinStatusComparison(master=root)
    frame = ttk.Frame(root)
    status_frame = StatusFrame(frame)
    compare_frame = CompareFrame(root)
    select_frame = SelectFrame(
        frame, snipper, status_frame.select_image)

    frame.pack()
    select_frame.pack(side=tk.LEFT, fill=tk.Y)
    status_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
    compare_frame.pack()

    # 表示
    root.mainloop()


def block_matching():
    snipper = ImageSnipper()
    input("1枚目")
    snip_img1 = snipper.Snip()
    w = snip_img1.width
    snip_img1 = snip_img1.crop((0, 53, w, 623))
    input("2枚目")
    snip_img2 = snipper.Snip()
    snip_img2 = snip_img2.crop((0, 53, w, 623))
    # 592,622
    template = snip_img1.crop(
        (0, snip_img1.height - 31, snip_img1.width, snip_img1.height - 1))

    res = cv2.matchTemplate(pil2cv(snip_img2), pil2cv(
        template), cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = min_loc
    bottom_right = (top_left[0] + template.width, top_left[1]+template.height)

    result = pil2cv(snip_img2)
    cv2.rectangle(result, top_left, bottom_right, 255, 2)

    dst = Image.new('RGB', (w, snip_img1.height - 31 +
                            snip_img2.height - top_left[1]))
    dst.paste(snip_img1, (0, 0))
    dst.paste(snip_img2.crop((
        0, top_left[1], w, snip_img2.height)), (0, snip_img1.height - 31))

    plt.subplot(223).imshow(template)
    plt.subplot(221).imshow(snip_img1)
    plt.subplot(222).imshow(snip_img2)
    plt.subplot(224).imshow(dst)
    plt.show()


if __name__ == "__main__":
    # status_concat_main()
    status_window_main()
    # canvas_scroll_main()
    # test()
    # block_matching()
