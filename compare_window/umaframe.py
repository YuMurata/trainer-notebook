import cv2
from snip import ImageSnipper
from misc import pil2cv
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from typing import Callable, NamedTuple
from logger import init_logger

logger = init_logger(__name__)


class ButtonFunc(NamedTuple):
    status: Callable[[Image.Image], None]
    add: Callable[[], None]
    delete: Callable[[int], None]


class UmaFrame(tk.Frame):
    def __init__(self, master: tk.Widget, snipper: ImageSnipper,
                 button_func: ButtonFunc):
        super().__init__(master, bg='white')

        status_frame = tk.Frame(self)
        status_frame.pack(side=tk.LEFT, pady=5, fill=tk.BOTH, expand=True)
        self.status_button = ttk.Button(status_frame, text='画像取得ボタンを押してください')
        self.status_button.bind('<Button-1>', self.status_button_left_click)
        self.status_button.pack(expand=True, fill=tk.BOTH)

        controll_frame = tk.Frame(self)
        controll_frame.pack(side=tk.RIGHT, pady=5)

        add_button = ttk.Button(controll_frame, text='画像取得')
        add_button.bind('<Button-1>', self.add_button_left_click)
        add_button.bind('<Button-3>', self.add_button_right_click)
        delete_button = ttk.Button(controll_frame, text='削除')
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
        print(self.winfo_width())
        print(self.status_button.winfo_width())
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
        bt_width = self.status_button.winfo_width()-10
        bt_height = self.status_button.winfo_height()-10
        if bt_width/bt_height < concat_img.width/concat_img.height:
            concat_img = concat_img.resize(
                (bt_width, int(concat_img.height/concat_img.width*bt_width)))
        else:
            concat_img = concat_img.resize(
                (int(concat_img.width/concat_img.height*bt_height), bt_height))

        # concat_img = concat_img.resize(
        #     (int(concat_img.width/1.5), int(concat_img.height/1.5)))

        self.bt_img = ImageTk.PhotoImage(image=concat_img)
        self.status_button.configure(image=self.bt_img)
