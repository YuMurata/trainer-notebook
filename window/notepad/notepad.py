from exception import IllegalInitializeException
import tkinter as tk
from tkinter import ttk, messagebox
from .define import notepad_dir
from typing import Callable,  NamedTuple


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

        self.listbox.bind('<<ListboxSelect>>', self.left_click)

        scroll_y = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll_y.pack(side=tk.RIGHT, fill="y")
        self.listbox["yscrollcommand"] = scroll_y.set

        self.reload_list()

    def reload_event(self, event):
        self.reload_list()

    def reload_list(self):
        self.listbox.delete(0, tk.END)

        for path in notepad_dir.iterdir():
            if path.suffix != '.txt':
                continue

            self.addList(path.stem)

    def addList(self, filename):
        self.listbox.insert(tk.END, filename)

    def left_click(self, event):
        itemIdxList = self.listbox.curselection()
        if len(itemIdxList) == 1:
            filename = self.listbox.get(itemIdxList)
            with open(notepad_dir/f'{filename}.txt', mode='r') as f:
                text = f.read()
            self.load_file(filename, text)

    def set_load_func(self, load_file):
        self.load_file = load_file


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

        self.isvisible = False
        # self.textbox.pack_forget()

    def clear_text(self):
        # self.textbox.insert(tk.END, 'test')
        if self.get_text() != '':
            self.textbox.delete(1.0, tk.END)

    def get_text(self):
        return self.textbox.get("1.0", 'end-1c')

    def set_text(self, str):
        self.clear_text()
        self.textbox.insert(1.0, str)


class ManageNotePadFrame(ttk.Frame):
    def __init__(self, master: tk.Widget, get_text: Callable[[], None], clear_text: Callable[[], None], reload: Callable[[], None]):
        super().__init__(master=master)

        self.edit_file: str = None
        self.get_text = get_text
        self.clear_text = clear_text
        self.reload = reload

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

        self.change_button.bind('<Button-1>', self._rename)

        self.delete_button = ttk.Button(self, text='delete')
        self.delete_button.pack(side=tk.LEFT)
        self.delete_button.bind('<Button-1>', self._delete)

        self.reload_button = ttk.Button(self, text='reload')
        self.reload_button.pack(side=tk.LEFT)
        self.reload_button.bind('<Button-1>', self.reload)

    def load_file(self, text_name: str):
        self.org_text_name = text_name
        self.text_name_var.set(text_name if text_name else '')
        self.edit_file = text_name

    def save(self, filename):
        if not self.edit_file:
            return
        with open(notepad_dir/f'{self.edit_file}.txt', mode='w') as f:
            f.write(self.get_text())

    def _new(self, event: tk.Event):
        edit_file = self.entry.get()
        if edit_file == '':
            return
        self.edit_file = edit_file
        self.clear_text()
        with open(notepad_dir/f'{self.edit_file}.txt', mode='w') as f:
            pass
        self.reload(event)

    def _rename(self, event: tk.Event):

        new_name = self.get_str()
        if new_name == '':
            messagebox.showerror('error', 'not set name')
            return

        org_path = notepad_dir/f'{self.edit_file}.txt'
        dst_path = notepad_dir/f'{new_name}.txt'
        org_path.rename(dst_path)
        self.edit_file = new_name
        self.reload(event)

    def _delete(self, event):
        if not self.edit_file:
            messagebox.showerror('delete', 'not select image')
            return

        if not messagebox.askokcancel('delete',
                                      f'delete {self.edit_file} ?'):
            return

        org_path = notepad_dir/f'{self.edit_file}.txt'
        org_path.unlink(True)

        self.reload(event)

    def get_str(self):
        return self.entry.get()


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
            self, textbox_frame.get_text, textbox_frame.clear_text, listbox_frame.reload_event)
        manage_frame.pack()

        def load_file(filename, text):
            textbox_frame.set_text(text)
            manage_frame.load_file(filename)

        listbox_frame.set_load_func(load_file)
