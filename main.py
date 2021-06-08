import tkinter as tk
from window import Win1
from TeamStadiumInfoDetection import TeamStadiumInfoDetection

if __name__ == "__main__":
    root = tk.Tk()#GUIのやつ
    app = Win1(master=root)

    def loop():
        if app.app2 is not None:
            app.app2.display()
        root.after(1000,loop)

    root.after(1000,loop)

    # 表示
    root.mainloop()
    print("roop end")
