from unittest import TestCase

import tkinter as tk
import main2 as Czekaj


class TestHomeWindow(TestCase):

    def setUp(self):
        window_size = (400, 650)
        self.root = tk.Tk()
        if not window_size:  # root.attributes('-zoomed', True)
            width, height = self.root.wm_maxsize()  # == root.winfo_screenwidth()
        else:
            width, height = window_size
        # root.attributes('-fullscreen', True)
        # root.resizable(0, 0)
        self.root.geometry(f'{width}x{height}+{self.root.wm_maxsize()[0] - width}+0')
        self.root.update()  # no mainloop yet
        self.root.title('mgr Alka Czekaja. ten program: Eryk Czekaj × Mateusz Grzywacz')
        self.blur_app = Czekaj.HomeWindow(self.root, (self.root.winfo_width(), self.root.winfo_height()),
                                          ['1.jpg', '2.jpg'])

    def test_unblur(self):
        def generate_heat(event):
            if event.char >= '0' and event.char <= '9':
                heat = int(event.char) / 10
                if event.char == '0':
                    heat = 1.0
                self.blur_app.unblur(heat)

        self.root.bind('<Key>', generate_heat)

        self.root.mainloop()
