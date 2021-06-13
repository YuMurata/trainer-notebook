import tkinter as tk
from window import Win1

if __name__ == "__main__":
    root = tk.Tk()  # GUIのやつ

    app = Win1(master=root)

    def loop():
        if app.score_app:
            app.score_app.display()
        root.after(1000, loop)

    root.after(1000, loop)

    # 表示
    root.mainloop()
