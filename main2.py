from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from math import sqrt
from random import random
from colour import Color

# Image 2 is on top of image 1.


# IMAGE1_DIR = "X:/python/obrazy/1.jpg"
# IMAGE2_DIR = "X:/python/obrazy/2.jpg"

# Brush size in pixels.
BRUSH = 45


# Actual size is 2*BRUSH


def create_image(filename, width, height):
    """
    Returns a PIL.Image object from filename - sized
    according to width and height parameters.

    filename: str.
    width: int, desired image width.
    height: int, desired image height.

    1) If neither width nor height is given, image will be returned as is.
    2) If both width and height are given, image will resized accordingly.
    3) If only width or only height is given, image will be scaled so specified
    parameter is satisfied while keeping image's original aspect ratio the same.
    """
    # Create a PIL image from the file.
    img = Image.open(filename, mode="r")
    img.putalpha(255)

    # Resize if necessary.
    if not width and not height:
        return img
    elif width and height:
        return img.resize((int(width), int(height)), Image.ANTIALIAS)
    else:  # Keep aspect ratio.
        w, h = img.size
        scale = width / float(w) if width else height / float(h)
        return img.resize((int(w * scale), int(h * scale)), Image.ANTIALIAS)


class Home(object):
    """
    master: tk.Tk window.
    screen: tuple, (width, height).
    """

    def __init__(self, master, screen):
        self.screen = w, h = screen
        self.master = master

        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.can = tk.Canvas(self.frame, width=w, height=h)
        self.can.pack()

        self.fname1 = filedialog.askopenfilename()
        self.fname2 = filedialog.askopenfilename()
        self.image1 = create_image(self.fname1, w, h)
        self.image2 = create_image(self.fname2, w, h)
        self.image3 = create_image(self.fname2, w, h)

        # Center of screen.
        self.center = w // 2, h // 2
        # Start with no photo on the screen.
        self.photo = False

        # Draw photo on screen.
        self.draw()

        # Key bindings.
        self.master.bind("<Return>", self.reset)
        # self.master.bind("<Motion>", self.erase)

        self.pos = []

        # for creating self transparent rectangles
        self.images = []

        # declare a heatmap
        self.map = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0.2, 0.2, 0, 0],
            [0, 0, 0.2, 0.2, 0, 0],
            [0, 0, 0.4, 0.4, 0, 0],
            [0, 0, 0.4, 0.4, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]

        # size of heatmap tiles in pixels based on self.map 2d list and size of an image
        self.heat_w = self.screen[0] // len(self.map[0])
        self.heat_h = self.screen[1] // len(self.map)

        # value of targeted areas
        self.mask = 0

        # mask_list populates with indexes of matching values with self.mask after erase function is called
        self.mask_list = []
        self.heat()
        self.erase(0, 0)

    def draw(self):
        """
        If there is a photo on the canvas, destroy it.
        Draw self.image2 on the canvas.
        """
        if self.photo:
            self.can.delete(self.photo)
            self.label.destroy()

        p = ImageTk.PhotoImage(image=self.image2)
        self.photo = self.can.create_image(self.center, image=p)
        self.label = tk.Label(image=p)
        self.label.image = p

    # Key Bindings #################
    def reset(self, event):
        """ Enter/Return key. """
        self.frame.destroy()
        self.__init__(self.master, self.screen)

    # def erase(self, event):
    def erase(self, a, b):
        """
        Mouse motion binding.
        Erase part of top image (self.photo2) at location (event.x, event.y),
        consequently exposing part of the bottom image (self.photo1).
        n - number of circles shown at any moment of time
        """

        # a, b = event.x, event.y
        r = BRUSH
        self.pos.append((a, b))
        n = 60
        # mask_list = [(i for i, x in enumerate(self.map)) if x == self.mask]

        for j in range(len(self.map)):
            for i, x in enumerate(self.map[j]):
                if x == self.mask:
                    self.mask_list.append([i, j])
        print(self.mask_list)
        for coords in self.mask_list:
            a = coords[0] * self.heat_w + self.heat_w // 2
            b = coords[1] * self.heat_h + self.heat_h // 2
            for x in range(a - r, a + r + 1):
                for y in range(b - r, b + r + 1):
                    try:
                        '''
                        if (x - a) * (x - a) + (y - b) * (y - b) <= r * r * random() ** 2:  # version with organized grid
                            p = self.image1.getpixel((x, y))
                            self.image2.putpixel((x, y), p)
                        elif r * r * 0.04 < (x - a) * (x - a) + (y - b) * (y - b) <= r * r * 0.16:
                            if x % 2 == 0 or y % 2 == 0:
                                p = self.image1.getpixel((x, y))
                                self.image2.putpixel((x, y), p)
                        elif r * r * 0.16 < (x - a) * (x - a) + (y - b) * (y - b) <= r * r * 0.36:
                            if x % 3 == 0 or y % 3 == 0:
                                p = self.image1.getpixel((x, y))
                                self.image2.putpixel((x, y), p)
                        elif r * r * 0.36 < (x - a) * (x - a) + (y - b) * (y - b) <= r * r * 0.64:
                            if x % 4 == 0 or y % 4 == 0:
                                p = self.image1.getpixel((x, y))
                                self.image2.putpixel((x, y), p)
                        elif r * r * 0.64 < (x - a) * (x - a) + (y - b) * (y - b) <= r * r:
                            if x % 5 == 0 or y % 5 == 0:
                                p = self.image1.getpixel((x, y))
                                self.image2.putpixel((x, y), p)
                                '''
                        if (x - a) * (x - a) + (y - b) * (
                                y - b) <= r * r * random() ** 2:  # version with random gradient
                            p = self.image1.getpixel((x, y))
                            self.image2.putpixel((x, y), p)

                    except IndexError:
                        pass

        # Returning back to original image
        if len(self.pos) > n:
            for x in range(self.pos[0][0] - r, self.pos[0][0] + r + 1):
                for y in range(self.pos[0][1] - r, self.pos[0][1] + r + 1):
                    try:
                        if (
                                (x - self.pos[0][0]) * (x - self.pos[0][0]) + (y - self.pos[0][1]) * (
                                y - self.pos[0][1]) <= r * r
                                and random() > 0.7
                        ):
                            q = self.image3.getpixel((x, y))
                            self.image2.putpixel((x, y), q)
                    except IndexError:
                        pass
            self.pos.pop(0)
        # print(self.pos)
        self.draw()
        self.heat()

    # creating semi-transparent images
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.master.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2 - x1, y2 - y1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.can.create_image(x1, y1, image=self.images[-1], anchor='nw')
        self.can.create_rectangle(x1, y1, x2, y2, **kwargs)

    # draw a heatmap
    def heat(self):
        for h in range(len(self.map)):
            for w in range(len(self.map[0])):
                color = Color(hsl=(self.map[h][w], 1, 0.5))
                self.create_rectangle(w * self.heat_w, h * self.heat_h,
                                      w * self.heat_w + self.heat_w, h * self.heat_h + self.heat_h, fill="%s" % color,
                                      alpha=.5)


def main(screen=(720, 1024)):
    root = tk.Tk()
    root.resizable(0, 0)
    Home(root, screen)
    root.mainloop()


if __name__ == '__main__':
    main()

# amateusz has changes a lot… (test)