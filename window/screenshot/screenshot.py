from exception import IllegalInitializeException
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, NamedTuple, Tuple, Dict, List
from snip import ImageSnipper
from window.image import Emphasis, ImageStruct, ImageStructDict
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw
from window.zoomable_canvas import ZoomableCanvasFrame

screenshot_dir = Path('./resource/user/screenshot')
screenshot_dir.mkdir(parents=True, exist_ok=True)

LoadImage = Callable[[], None]


class TakeFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self.snipper = ImageSnipper()

        self.take_image: ImageStruct = None
        self.item_id: int = None

        button_frame = self._create_button(self)
        button_frame.pack()

        snip_width, snip_height = ImageSnipper.snip_size
        self.canvas = tk.Canvas(
            self, width=snip_width, height=snip_height)
        self.canvas.pack()

        self.load_image: LoadImage = None

    def _create_button(self, master: tk.Widget):
        frame = ttk.Frame(master)
        take_button = ttk.Button(frame, text='take')
        take_button.pack(side=tk.LEFT)
        take_button.bind('<Button-1>', self._take)

        save_button = ttk.Button(frame, text='save')
        save_button.pack(side=tk.LEFT)
        save_button.bind('<Button-1>', self._save)

        return frame

    def _take(self, event):
        image = self.snipper.Snip()
        if not image:
            return

        self.take_image = ImageStruct(image)
        self.item_id = self.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.take_image.photoimage)

    def set_load_image(self, load_image: LoadImage):
        self.load_image = load_image

    def _save(self, event):
        if not self.load_image:
            raise IllegalInitializeException('load_image not set')

        if not self.take_image:
            messagebox.showerror('error', 'not take image')
            return

        now = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.take_image.image.save(str(screenshot_dir/f'{now}.png'))

        self.load_image()


class NameChangeFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        label = ttk.Label(self, text='image name: ')
        label.pack(side=tk.LEFT)

        self.image_name_var = tk.StringVar(self)
        self.entry = ttk.Entry(self, textvariable=self.image_name_var)
        self.entry.bind('<Return>', self._save)
        self.entry.pack(side=tk.LEFT)

        label = ttk.Label(self, text='.png')
        label.pack(side=tk.LEFT)

        button = ttk.Button(self, text='name change')
        button.pack(side=tk.LEFT)

        button.bind('<Button-1>', self._save)

        self.org_image_name: str = None
        self.load_image: LoadImage = None

    def set_image_name(self, image_name: str):
        self.org_image_name = image_name
        self.image_name_var.set(image_name)

    def _save(self, event: tk.Event):
        if not self.load_image:
            raise IllegalInitializeException('load_image not set')

        if not self.org_image_name:
            return

        image_name = self.image_name_var.get()
        if image_name == '':
            messagebox.showerror('error', 'not set name')
            return

        org_path = screenshot_dir/f'{self.org_image_name}.png'
        dst_path = screenshot_dir/f'{image_name}.png'
        org_path.rename(dst_path)
        self.load_image()

    def set_load_image(self, load_image: LoadImage):
        self.load_image = load_image


class PrevSelect(NamedTuple):
    item_id: int
    image_struct: ImageStruct


class ViewFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self.name_change_frame = NameChangeFrame(self)
        self.name_change_frame.set_load_image(self.load_image)
        self.name_change_frame.pack()

        width, height = ImageSnipper.snip_size
        width *= 2.2

        self.image_dict = ImageStructDict()
        self.name_dict: Dict[int, str] = dict()

        self.canvas_frame = ZoomableCanvasFrame(
            self, self.image_dict, self._get_image_xy,
            canvas_option={'bg': 'white', 'width': width, 'height': height})
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = self.canvas_frame.canvas
        self.canvas.tag_bind('screenshot', '<Button-1>', self._get_image_name)

        self.load_image()
        self.prev_id: int = None

    def _get_image_name(self, event: tk.Event):
        x, y = self.canvas_frame.canvas_xy(event)

        item_id_list: List[int] = self.canvas.find_closest(x, y)

        if len(item_id_list) < 1:
            return

        item_id = item_id_list[0]

        if self.prev_id:
            prev_image = self.image_dict[self.prev_id]
            prev_image.set_emphasis(None)
            self.canvas.itemconfig(self.prev_id, image=prev_image.photoimage)

        image_struct = self.image_dict[item_id]
        image_struct.set_emphasis(Emphasis(3, (0, 200, 0)))
        self.canvas.itemconfig(item_id, image=image_struct.photoimage)

        image_name = self.name_dict[item_id]
        self.name_change_frame.set_image_name(image_name)

        self.prev_id = item_id

    def load_image(self):
        for item_id in self.image_dict.keys():
            self.canvas.delete(item_id)

        self.image_dict.clear()
        self.name_dict.clear()

        old_item_id: int = None
        for image_path in screenshot_dir.iterdir():
            if image_path.suffix != '.png':
                continue

            image_struct = ImageStruct(Image.open(image_path))

            item_id = self.canvas.create_image(self._get_image_xy(
                old_item_id), anchor=tk.NW, image=image_struct.photoimage,
                tags='screenshot')
            old_item_id = item_id

            self.image_dict[item_id] = image_struct
            self.name_dict[item_id] = image_path.stem

        self.canvas_frame.reconfig_scroll()
        self.prev_id = None

    def _get_image_xy(self, item_id: int) -> Tuple[int, int]:
        if not item_id:
            return 0, 0

        pad = 10

        x = self.canvas.bbox(item_id)[2] + pad
        y = self.canvas.bbox(item_id)[1]

        threshold_x = 700
        if x > threshold_x:
            x = 0
            y = self.canvas.bbox(item_id)[3]+pad

        return x, y


class ScreenShotFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self.tab = ttk.Notebook(self, width=-1, height=-1)
        self.tab.pack(expand=True, fill=tk.BOTH)

        take_frame = TakeFrame(self)
        self.tab.add(take_frame, text='take')

        view_frame = ViewFrame(self)
        self.tab.add(view_frame, text='view')

        take_frame.set_load_image(view_frame.load_image)
