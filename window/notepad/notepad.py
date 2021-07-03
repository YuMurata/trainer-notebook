from exception import IllegalInitializeException
import tkinter as tk
from tkinter import ttk, messagebox
from .define import notepad_dir
from typing import Callable,  NamedTuple


class TextFunc(NamedTuple):
    new: Callable[[], None]
    save: Callable[[], None]
    delete: Callable[[], None]
    update: Callable[[], None]


class ManageNotePadFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        label = ttk.Label(self, text='notepad name: ')
        label.pack(side=tk.LEFT)

        self.image_name_var = tk.StringVar(self)
        self.entry = ttk.Entry(self, textvariable=self.image_name_var)
        self.entry.bind('<Return>', self._save)
        self.entry.pack(side=tk.LEFT)

        label = ttk.Label(self, text='.png')
        label.pack(side=tk.LEFT)

        new_button = ttk.Button(self, text='new')
        new_button.bind('<Button-1>', self._new)
        new_button.pack(side=tk.LEFT)

        change_button = ttk.Button(self, text='name change')
        change_button.pack(side=tk.LEFT)

        change_button.bind('<Button-1>', self._save)

        delete_button = ttk.Button(self, text='delete')
        delete_button.pack(side=tk.LEFT)
        delete_button.bind('<Button-1>', self._delete)

        update_button = ttk.Button(self, text='update')
        update_button.pack(side=tk.LEFT)
        update_button.bind('<Button-1>', self._update)

        self.edit_file: str = None

    def set_image_name(self, image_name: str):
        self.org_image_name = image_name
        self.image_name_var.set(image_name if image_name else '')

    def _new(self, event: tk.Event):
        pass

    def _save(self, event: tk.Event):

        image_name = self.image_name_var.get()
        if image_name == '':
            messagebox.showerror('error', 'not set name')
            return

        org_path = screenshot_dir/f'{self.org_image_name}.png'
        dst_path = screenshot_dir/f'{image_name}.png'
        org_path.rename(dst_path)
        self.load_image()

    def _delete(self, event):
        if not self.org_image_name:
            messagebox.showerror('delete', 'not select image')
            return

        if not messagebox.askokcancel('delete',
                                      f'delete {self.org_image_name} ?'):
            return

        org_path = screenshot_dir/f'{self.org_image_name}.png'
        org_path.unlink(True)

        self.set_image_name(None)

    def _update(self, event):
        pass

    def load_text(self):
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


class NotePadListBox(tk.Listbox):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)


class ListFrame(tk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self._create_widget()

    def _create_widget(self):

        self.listbox = tk.Listbox(self)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)

        scroll_y = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll_y.pack(side=tk.RIGHT, fill="y")
        self.listbox["yscrollcommand"] = scroll_y.set

        self.update_list()

    def update_list(self):
        self.listbox.delete(0, tk.END)

        for path in notepad_dir.iterdir():
            if path.suffix != '.txt':
                continue

            self.addList(path.stem)

    def addList(self, filename):
        self.listbox.insert(tk.END, filename)


class TextBoxFrame(tk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self._create_widget()

    def _create_widget(self):
        frame = tk.Frame(self)
        frame.pack()

        textbox = tk.Text(frame, wrap=tk.NONE)
        textbox.pack(side=tk.LEFT)

        scroll_y = tk.Scrollbar(
            frame, orient=tk.VERTICAL, command=textbox.yview)
        scroll_y.pack(side=tk.RIGHT, fill="y")

        scroll_x = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=textbox.xview)
        scroll_x.pack(side=tk.BOTTOM, fill="x")

        # 動きをスクロールバーに反映
        textbox["yscrollcommand"] = scroll_y.set
        textbox["xscrollcommand"] = scroll_x.set


class NotePadFrame(tk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self._create_widget()

    def _create_widget(self):

        listbox_frame = ListFrame(self)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        textbox_frame = TextBoxFrame(self)
        textbox_frame.pack(padx=5)

        manage_frame = ManageNotePadFrame(self)
        manage_frame.pack()
