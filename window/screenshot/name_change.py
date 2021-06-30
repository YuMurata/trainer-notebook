from exception import IllegalInitializeException
import tkinter as tk
from tkinter import ttk, messagebox
from .define import LoadImage, screenshot_dir


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
