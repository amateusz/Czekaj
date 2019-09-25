from PIL import Image, ImageTk, ImageColor
import tkinter as tk
from tkinter import filedialog
from math import sqrt
from random import random, shuffle, randint
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


class BlurApp():
    """
    master: tk.Tk window.
    screen: tuple, (width, height).
    """
    PURPLE = tuple([int((255 ** 2) * _) for _ in Color('purple').get_rgb()])

    def __init__(self, master, canvas_size, filenames=None):
        self.canvas_size = canvas_size  # policy: everything stretched to fill this size. no aspect preservation
        self.parent = master

        self.frame = tk.Frame(self.parent)
        self.frame.pack()
        self.canvas = tk.Canvas(self.frame, width=self.canvas_size[0], height=self.canvas_size[1])
        self.canvas.pack()

        self.loadImages(filenames)

        # Center of screen.
        self.center = self.canvas_size[0] // 2, self.canvas_size[1] // 2
        # Start with no photo on the screen.
        self.photo = False

        self.pos = []

        # for creating self transparent rectangles
        self.images = []

        # declare a heatmap
        self.heatmap_alpha_auto = 0

        # if both lists are empty, the the state is _steady_/_idle_ ^^.
        self.tiles_to_unblur = []
        self.splats_to_blur = []

        # task retention
        self.flush_blur_waypoints_task = None
        self.bg_blur_task = None

        self.HEATMAP = [
            [0.1, 0.1, 0.40, 0.60, 0.24, 0.1],
            [0.1, 0.18, 0.30, 0.50, 0.2, 0.1],
            [0.1, 0.15, 0.35, 0.45, 0.2, 0.1],
            [0.1, 0.15, 0.35, 0.40, 0.2, 0.1],
            [0.1, 0.1, 0.30, 0.35, 0.18, 0.1],
            [0.1, 0.1, 0.20, 0.30, 0.17, 0.1],
            [0.1, 0.1, 0.15, 0.25, 0.16, 0.1],
            [0.1, 0.1, 0.15, 0.20, 0.13, 0.1],
            [0.1, 0.1, 0.10, 0.10, 0.12, 0.1],
        ]

        # size of heatmap tiles in pixels based on self.map 2d list and size of an image
        self.heat_tile_w = self.canvas_size[0] / len(self.HEATMAP[0])
        self.heat_tile_h = self.canvas_size[1] / len(self.HEATMAP)

        # value of targeted areas
        self.mask = .1

        # mask_list populates with indexes of matching values with self.mask after erase function is called
        self.mask_list = []
        # self.heat()
        # self.unblur()

        # Key bindings.
        self.parent.bind('<Button-1>', self.click_callback)
        self.parent.bind("<Return>", self.reset)
        self.parent.bind('<Escape>', self.parent.destroy)
        self.parent.bind("<Motion>", self.unblur_mouse)

        # Draw photo on screen.
        self.draw()

    def click_callback(self, event):
        if event.num == 1:
            self.heatmap_alpha_auto += 1 / 3
            self.heatmap_alpha_auto %= 1.01
            self.draw()

    def loadImages(self, filenames=None):
        if not filenames or len(filenames) != 2:
            fname1 = filedialog.askopenfilename()
            fname2 = filedialog.askopenfilename()
        else:
            fname1 = filenames[0]
            fname2 = filenames[1]
        self.image_clear = create_image(fname1, width=self.canvas_size[0], height=self.canvas_size[1])
        self.image_working = create_image(fname2, width=self.canvas_size[0], height=self.canvas_size[1])
        self.image_blurred = create_image(fname2, width=self.canvas_size[0], height=self.canvas_size[1])

    def draw(self):
        """
        If there is a photo on the canvas, destroy it.
        Draw self.image_working on the canvas.
        """
        if self.photo:
            self.canvas.delete(self.photo)
            self.label.destroy()

        p = ImageTk.PhotoImage(image=self.image_working)
        self.photo = self.canvas.create_image(self.center, image=p)
        self.label = tk.Label(image=p)
        self.label.image = p
        if self.heatmap_alpha_auto:
            self.heat()

    # Key Bindings #################
    def reset(self, event):
        """ Enter/Return key. """
        self.frame.destroy()
        self.__init__(self.parent, self.canvas_size)

    def flush_unblur_waypoints(self):
        if len(self.tiles_to_unblur) > 0:
            tile = self.tiles_to_unblur.pop()
            splat_centre = self.tile_to_abs(tile, .55)
            self.unblur(*splat_centre)
            self.frame.after(90, self.flush_unblur_waypoints)

    def flush_blur_waypoints(self):
        if len(self.splats_to_blur) > 0:
            splat_centre = self.splats_to_blur.pop(0)  # so the reverse order
            self.blur(*splat_centre, .25)
            self.flush_blur_waypoints_task = self.frame.after(130, self.flush_blur_waypoints)
        else:
            self.flush_blur_waypoints_task = None
            self.blur_random()

    def unblur_tile_routeplanner(self, heat):
        """  it works like this:
        with each unit there happens one unblur(heat) call.
        this call is supposed to uncover _some_ of the surface of heat value of ≤
        """
        # prepare list of tiles of the heat and below
        # not_hotter_tiles = [True for tile in [row for row in self.HEATMAP] if tile <= heat]

        # here we'll collect results that should be unblurred
        hot_enough = []

        for row in range(len(self.HEATMAP)):
            for column, value in enumerate(self.HEATMAP[row]):
                if value <= heat:
                    hot_enough.append([column, row])
        # shuffle resulting list
        shuffle(hot_enough)
        # turncate resulting list
        hot_enough = hot_enough[:int(len(hot_enough) * .35)]  # 35% will stay
        # generate a path through remaining waypoints
        self.tiles_to_unblur = hot_enough
        self.flush_unblur_waypoints()

    def tile_to_abs(self, heat_tile, randomize=False):
        a = heat_tile[0] * self.heat_tile_w
        b = heat_tile[1] * self.heat_tile_h
        if not randomize:
            # put at the centre
            a += self.heat_tile_w / 2
            b += self.heat_tile_h / 2
        else:
            # put anywhre in the self.heat_tile_| plane
            a += random() * self.heat_tile_w * randomize
            b += random() * self.heat_tile_h * randomize
        return int(a), int(b)

    def unblur_mouse(self, event):
        self.unblur(event.x, event.y)

    def unblur(self, a, b):
        """
        Mouse motion binding.
        Erase part of top image (self.photo2) at location (event.x, event.y),
        consequently exposing part of the bottom image (self.photo1).
        n - number of circles shown at any moment of time
        """

        self.splats_to_blur.append((a, b))

        # a, b = event.x, event.y
        r = BRUSH

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
                    if (x - a) * (x - a) + (y - b) * (y - b) \
                            <= (r / 2) ** 2 * ((random() * 1.5) ** 3):  # version with random gradient
                        color = self.image_clear.getpixel((x, y))
                        self.image_working.putpixel((x, y), color)
                    try:
                        if __class__.debug_cursors:
                            if (x - a) * (x - a) + (y - b) * (y - b) \
                                    >= (r / 2.0) ** 2 \
                                    and \
                                    (x - a) * (x - a) + (y - b) * (y - b) \
                                    <= (r / 1.9) ** 2:
                                color = __class__.PURPLE
                                self.image_working.putpixel((x, y), color)
                    except:
                        pass

                except IndexError:
                    pass
        self.draw()

        # if pending, then cancel.
        if self.flush_blur_waypoints_task:
            self.frame.after_cancel(self.flush_blur_waypoints_task)
        # schedule it for 3sec from now. If a movement will happen, move the window.
        self.flush_blur_waypoints_task = self.frame.after(3000, self.flush_blur_waypoints)

        # also cancel pending bg blur
        if self.bg_blur_task:
            self.frame.after_cancel(self.bg_blur_task)

    def blur_random(self, at_once=10):
        '''
        sparkling random fixing of the image
        :param delay: in [ms]
        :return:
        '''

        delay = 350

        for i in range(at_once):
            x, y = [randint(0, _ - 1) for _ in self.canvas_size]
            color = self.image_blurred.getpixel((x, y))
            try:
                if __class__.debug_cursors:
                    color = __class__.PURPLE
            except:
                pass

            self.image_working.putpixel((x, y), color)
        self.bg_blur_task = self.frame.after(delay, self.blur_random)
        self.draw()

    def blur(self, a, b, effectivness=1.0):
        '''
        blurs back the image to the default state
        let's sey it works like this:
        it randomly restores pixels to the original, which are inside no matter which were set
        :return:
        '''

        r = BRUSH
        # Returning back to original image

        for x in range(a - r, a + r + 1):
            for y in range(b - r, b + r + 1):
                try:
                    if (x - a) ** 2 + (y - b) ** 2 <= r ** 2:
                        if effectivness != 1.0:
                            if random() > effectivness:
                                continue
                        color = self.image_blurred.getpixel((x, y))
                        self.image_working.putpixel((x, y), color)
                        try:
                            if __class__.debug_cursors:
                                if (x - a) ** 2 + (y - b) ** 2 <= r ** 2 and \
                                        (x - a) ** 2 + (y - b) ** 2 >= (r * .95) ** 2:
                                    color = __class__.PURPLE
                                self.image_working.putpixel((x, y), color)
                        except:
                            pass

                except IndexError:
                    pass
        self.draw()

    # creating semi-transparent images
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill_mixed = ImageColor.getrgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2 - x1, y2 - y1), fill_mixed)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(x1, y1, image=self.images[-1], anchor='nw')
        self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    # draw a heatmap
    def heat(self):
        for vertical in range(len(self.HEATMAP)):
            for horizontal in range(len(self.HEATMAP[0])):
                color = Color(hsl=(.9, 1, self.HEATMAP[vertical][horizontal] / 2))
                self.create_rectangle(int(horizontal * self.heat_tile_w), \
                                      int(vertical * self.heat_tile_h), \
                                      int(horizontal * self.heat_tile_w + self.heat_tile_w), \
                                      int(vertical * self.heat_tile_h + self.heat_tile_h), \
                                      fill="%s" % color, alpha=self.heatmap_alpha_auto)


def main(window_size=None):
    root = tk.Tk()
    if not window_size:  # root.attributes('-zoomed', True)
        width, height = root.wm_maxsize()  # == root.winfo_screenwidth()
    else:
        width, height = window_size
    # root.attributes('-fullscreen', True)
    # root.resizable(0, 0)
    root.geometry(f'{width}x{height}+{root.wm_maxsize()[0] - width}+0')
    root.update()  # no mainloop yet
    root.title('mgr Alka Czekaja. ten program: Eryk Czekaj × Mateusz Grzywacz')
    blur_app = BlurApp(root, (root.winfo_width(), root.winfo_height()), ['1.jpg', '2.jpg'])
    root.mainloop()


if __name__ == '__main__':
    main((500, 800))

# amateusz has changes a lot… (test)
