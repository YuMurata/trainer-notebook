from exception import IllegalInitializeException
import tkinter as tk
from tkinter import ttk, messagebox
from .define import notepad_dir
from typing import Callable,  NamedTuple


class TextFunc(NamedTuple):
    new: Callable[[], None]
    save: Callable[[], None]
    delete: Callable[[], None]
    reload: Callable[[], None]


class ManageNotePadFrame(ttk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        label = ttk.Label(self, text='notepad name: ')
        label.pack(side=tk.LEFT)

        self.text_name_var = tk.StringVar(self)
        self.entry = ttk.Entry(self, textvariable=self.text_name_var)
        self.entry.pack(side=tk.LEFT)

        label = ttk.Label(self, text='.png')
        label.pack(side=tk.LEFT)

        self.new_button = ttk.Button(self, text='new')
        self.new_button.bind('<Button-1>', self._new)
        self.new_button.pack(side=tk.LEFT)

        self.change_button = ttk.Button(self, text='name change')
        self.change_button.pack(side=tk.LEFT)

        # self.change_button.bind('<Button-1>', self._save)

        self.delete_button = ttk.Button(self, text='delete')
        self.delete_button.pack(side=tk.LEFT)
        # self.delete_button.bind('<Button-1>', self._delete)

        self.reload_button = ttk.Button(self, text='reload')
        self.reload_button.pack(side=tk.LEFT)
        # self.reload_button.bind('<Button-1>', self.text_func.reload)

        self.edit_file: str = None

    def set_text_func(self, text_func: TextFunc):
        self.text_func = text_func
        self.new_button.bind('<Button-1>', self.text_func.new)
        self.change_button.bind('<Button-1>', self.text_func.save)
        self.delete_button.bind('<Button-1>', self.text_func.delete)
        self.reload_button.bind('<Button-1>', self.text_func.reload)

    def set_text_name(self, text_name: str):
        self.org_text_name = text_name
        self.text_name_var.set(text_name if text_name else '')

    def save(self, filename):
        if filename == '':
            messagebox.showerror('error', 'not set name')
            return
        text_name = self.text_name_var.get()

        org_path = notepad_dir/f'{self.org_text_name}.png'
        dst_path = notepad_dir/f'{text_name}.png'
        org_path.rename(dst_path)

    def _new(self, event: tk.Event):
        pass

    def _save(self, event: tk.Event):

        image_name = self.text_name_var.get()
        if image_name == '':
            messagebox.showerror('error', 'not set name')
            return

        org_path = notepad_dir/f'{self.org_image_name}.png'
        dst_path = notepad_dir/f'{image_name}.png'
        org_path.rename(dst_path)
        self.load_text()

    def _delete(self, event):
        if not self.org_image_name:
            messagebox.showerror('delete', 'not select image')
            return

        if not messagebox.askokcancel('delete',
                                      f'delete {self.org_image_name} ?'):
            return

        org_path = notepad_dir/f'{self.org_image_name}.png'
        org_path.unlink(True)

        self.load_text()

    def get_str(self):
        return self.entry.get()


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

        self.reload_list()

    def reload_list(self):
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

        self.textbox = tk.Text(frame, wrap=tk.NONE)
        self.textbox.pack(side=tk.LEFT)

        scroll_y = tk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self.textbox.yview)
        scroll_y.pack(side=tk.RIGHT, fill="y")

        scroll_x = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.textbox.xview)
        scroll_x.pack(side=tk.BOTTOM, fill="x")

        # 動きをスクロールバーに反映
        self.textbox["yscrollcommand"] = scroll_y.set
        self.textbox["xscrollcommand"] = scroll_x.set

    def clear_text(self):
        # self.textbox.insert(tk.END, 'test')
        if self.get_text() != '':
            self.textbox.delete(1, tk.END)

    def get_text(self):
        return self.textbox.get("1.0", 'end-1c')


class NotePadFrame(tk.Frame):
    def __init__(self, master: tk.Widget):
        super().__init__(master=master)

        self._create_widget()

    def _create_widget(self):

        listbox_frame = ListFrame(self)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        textbox_frame = TextBoxFrame(self)
        textbox_frame.pack(padx=5)

        manage_frame = ManageNotePadFrame(
            self)
        manage_frame.pack()

        def new_text(event):
            textbox_frame.clear_text()
            listbox_frame.reload_list()

        def save_text(event):
            pass

        def delete_text(event):
            pass

        def reload_text(event):
            pass

        manage_frame.set_text_func(
            TextFunc(new_text, save_text, delete_text, reload_text))
