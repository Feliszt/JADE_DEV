# GUI
from tkinter import *
import time

class MyClass :
    # init
    def __init__(self, _window) :
        # win
        self.win = _window
        self.win.overrideredirect(True)
        self.app_w = 100
        self.app_h = 100
        self.off_x = 10
        self.off_y = 10
        self.win.geometry("{}x{}+{}+{}".format(self.app_w, self.app_h, self.off_x, self.off_y))

        # canvas
        self.canvas = Canvas(self.win, width=self.app_w, height=self.app_h, bd=0, highlightthickness=0, relief='ridge', bg='black')
        self.canvas.pack(side = LEFT)
        
        self.update()
        self.win.mainloop()
        
    #
    def update(self) :
        #time.sleep(1)
        self.win.after(5, self.update)

# main function
if __name__ == "__main__" :
    MyClass(Tk())
