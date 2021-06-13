import tkinter as tk
from window import Win1

if __name__ == "__main__":
    root = tk.Tk()  # GUIのやつ

    app = Win1(master=root)

    # 表示
    root.mainloop()
