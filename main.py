import tkinter as tk
from window import Win1

if __name__ == "__main__":
    root = tk.Tk()  # GUIのやつ

    Win1(master=root).pack()

    # 表示
    root.mainloop()
