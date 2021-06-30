from exception import IllegalInitializeException
import tkinter as tk
from tkinter import ttk, messagebox
from snip import ImageSnipper
from window.image import ImageStruct
from datetime import datetime
from .define import LoadImage, screenshot_dir


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
