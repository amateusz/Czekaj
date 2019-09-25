from unittest import TestCase, FunctionTestCase, skipUnless
import sys

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
        self.blur_app = Czekaj.BlurApp(self.root, (self.root.winfo_width(), self.root.winfo_height()),
                                       ['1.jpg', '2.jpg'])
        self.root.title('mgr Alka Czekaja. ten program: Eryk Czekaj × Mateusz Grzywacz')
        Czekaj.BlurApp.debug_cursors = True

    def test_unblur(self):
        ''''
        press keys 0-9 in order to simulate _heat_
        '''

        def generate_heat(event):
            if event.char >= '0' and event.char <= '9':
                heat = int(event.char) / 10
                if event.char == '0':
                    heat = 1.0
                self.blur_app.unblur_tile_routeplanner(heat)

        self.root.bind('<Key>', generate_heat)
        self.root.mainloop()

    def test_blur_waypoints(self):
        splats = [[280, 300], [240, 40], [110, 170], [320, 100]]
        for splat in splats:
            self.blur_app.unblur(*splat)
        self.root.update()
        # self.root.after(3000, self.blur_app.flush_blur_waypoints)
        self.root.mainloop()

    def test_blur_backgroud(self):
        self.blur_app.image_working = self.blur_app.image_clear.copy()
        self.blur_app.draw()
        self.root.update()

        self.blur_app.blur_random(3000)
        self.root.mainloop()


class TestHomeWindowFullscreen(TestCase):

    def setUp(self):
        # self.root.attributes('-zoomed', True)
        self.root = tk.Tk()
        width, height = self.root.wm_maxsize()  # == root.winfo_screenwidth()
        self.root.attributes('-fullscreen', True)
        # root.resizable(0, 0)
        self.root.geometry(f'{width}x{height}+{self.root.wm_maxsize()[0] - width}+0')
        self.root.update()  # no mainloop yet
        self.blur_app = Czekaj.BlurApp(self.root, (self.root.winfo_width(), self.root.winfo_height()),
                                       ['1.jpg', '2.jpg'])
        self.root.title('mgr Alka Czekaja. ten program: Eryk Czekaj × Mateusz Grzywacz')
        # Czekaj.BlurApp.debug_cursors = True

    @skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_windows_support(self):
        # windows specific testing code
        pass

    def test_unblur(self):
        ''''
        press keys 0-9 in order to simulate _heat_
        '''

        def generate_heat(event):
            if event.char >= '0' and event.char <= '9':
                heat = int(event.char) / 10
                if event.char == '0':
                    heat = 1.0
                self.blur_app.unblur_tile_routeplanner(heat)

        self.root.bind('<Key>', generate_heat)
        self.root.mainloop()
