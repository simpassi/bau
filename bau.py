import os
import random
from PIL import Image, ImageDraw


class Bau(object):
    def __init__(self, grid_w=16, grid_h=16, resolution=1024, max_h=3, imageset="default"):
        self.res = resolution
        self.aa = 4  # anti-alias level
        self.w = self.res * self.aa
        self.h = self.res * self.aa
        self.grid_width = grid_w
        self.grid_height = grid_h
        self.grid = self.makegrid(grid_w, grid_h)
        self.max_h = max_h

        self.all_images = {}
        for a in os.listdir(imageset):
            if a.lower().endswith(".png") or a.lower().endswith(".jpg"):
                img = Image.open(os.path.join(imageset, a))
                # store the aspect ratio in 1/1, 1/2, 1/3 notation
                ratio = "1/{}".format(img.height / img.width)
                if ratio not in self.all_images:
                    self.all_images[ratio] = []
                self.all_images[ratio].append(img)

    def choose_block(self, w, h):
        ratio = "1/{}".format(h / w)
        if ratio in self.all_images:
            img = random.choice(self.all_images[ratio])
            if ratio == "1/1":
                return img.rotate(random.choice([0, 90, 180, 270]))
            else:
                return img.rotate(random.choice([0, 180]))
        return None

    def makegrid(self, w, h):
        ret = []
        for y in range(h):
            row = []
            for x in range(w):
                row.append(0)
            ret.append(row)
        return ret

    def yes(self):
        return random.uniform(0.0, 1.0) < 0.5

    def check(self, x, y, w, h):
        for ix in range(x, x + w):
            if ix >= self.grid_width:
                return False
            for iy in range(y, y + h):
                if iy >= self.grid_height:
                    return False
                if self.grid[iy][ix] != 0:
                    return False
        return True

    def markup(self, x, y, w, h, e):
        for ix in range(x, x + w):
            for iy in range(y, y + h):
                self.grid[iy][ix] = e

    def divide(self, ms):
        elems = []
        for y in range(0, self.grid_height):
            for x in range(0, self.grid_width):
                h = min(ms, min(random.randint(1, ms), self.grid_height - y))
                w = min(ms, min(random.choice([h, 1]), self.grid_width - x))
                store = True
                if not self.check(x, y, w, h):
                    w, h = 1, 1
                    if not self.check(x, y, w, h):
                        store = False
                if store:
                    self.markup(x, y, w, h, len(elems) + 1)
                    elems.append([x, y, w, h])
        return elems

    def bauhaus(self, i1, i2, x, y, w, h):
        resized = i2.resize((w, h))
        i1.paste(resized, [x, y, x + w, y + h])

    def generate(self, seed, path):
        random.seed(seed)
        canvas = Image.new("RGB", (self.w, self.h), "#FFFFFF")
        gs = self.grid_width
        elements = self.divide(self.max_h)
        for e in elements:
            x = e[0] * self.w / gs
            y = e[1] * self.h / gs
            sx = e[2] * self.w / gs
            sy = e[3] * self.h / gs
            elem = self.choose_block(sx, sy)
            if elem is not None:
                self.bauhaus(canvas, elem, x, y, sx, sy)

        canvas = canvas.resize((self.res, self.res), Image.BICUBIC)
        canvas.save(path)

if __name__ == "__main__":
    import sys
    res = 1024
    imageset = "default"
    gw = 16
    mh = 3
    seed = random.randint(1, 1024 * 1024)
    out_file = "out_{}.png".format(seed)
    if len(sys.argv)>1:
        for param in sys.argv[1:]:
            if param.startswith("-r="):
                res = int(param[3:])
            elif param.startswith("-i="):
                imageset = param[3:]
            elif param.startswith("-g="):
                gw = int(param[3:])
            elif param.startswith("-m="):
                mh = int(param[3:])
            elif param.startswith("-s="):
                seed = int(param[3:])
                out_file = "out_{}.png".format(seed)
            elif param.endswith(".png") or param.endswith(".jpg"):
                out_file = param
            
    bau = Bau(resolution=res, grid_w=gw, grid_h=gw, max_h=mh, imageset=imageset)
    bau.generate(seed, out_file)
    print("seed: {}".format(seed))
