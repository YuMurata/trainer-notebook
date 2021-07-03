import tkinter as tk
from window.notepad.notepad import NotePadFrame

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Notepad")

    app = NotePadFrame(root)
    app.pack()
    # app.pack()

    root.mainloop()
