__author__ = 'Grishnak'
from copy import deepcopy

# todo: Cythonize this file for  M A X I M U M   P E R F O R M A N C E !


class Light:
    def __init__(self, r=0.0, g=0.0, b=0.0, brightness=0.0):
        self.r = r
        self.g = g
        self.b = b
        self. brightness = brightness


class LightMask:
    def __init__(self, width, height, intensity=20.0, falloff=1.0, max_rad=2, ambient=0.05):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.falloff = falloff / intensity
        self.max_bur_rad = max_rad
        self.ambient = ambient
        self.mask = [(ambient, ambient, ambient) for i in range(width*height)]
        self.persistent_light_map = [(ambient, ambient, ambient) for i in range(width*height)]
        self.opacity = [ambient for i in range(width*height)]

    def idx(self, x, y):
        return (x + y * self.width)

    def get_mask_value(self, x, y):
        return self.mask[self.idx(x, y)]

    def reset(self):
        self.mask = [(self.ambient, self.ambient, self.ambient) for i in range(self.width*self.height)] # deepcopy(self.persistent_light_map)

    def set_opacity_value(self, x, y, o):
        self.opacity[self.idx(x, y)] = o

    def set_persistent_lightmask(self):
        self.persistent_light_map = deepcopy(self.mask)

    def add_light(self, x, y, br): #br should be a tuple with 3 variables, r, g, b values
        if not isinstance(br, tuple):
            br = (br, br, br)

        rmax = max(self.mask[self.idx(x,y)][0], br[0])
        bmax = max(self.mask[self.idx(x,y)][1], br[1])
        gmax = max(self.mask[self.idx(x,y)][2], br[2])
        br = (rmax, bmax, gmax)
        self.mask[self.idx(x,y)] = br

    def set_intensity(self, i):
        i =  max(1.0, i)
        self.intensity = i
        self.falloff = self.falloff/i

    def set_ambient(self, ambient):
        self.ambient = max(0.0, (min(1.0, ambient )))

    def compute_intensity(self, here, neighbor1, neighbor2, wall):
        local_falloff = min(1.0, self.falloff + (wall/10.0))

        n1r = max(here[0], neighbor1[0])
        n1g = max(here[1], neighbor1[1])
        n1b = max(here[2], neighbor1[2])

        n2r = max(here[0], neighbor2[0])
        n2g = max(here[1], neighbor2[1])
        n2b = max(here[2], neighbor2[2])

        r = max(self.ambient, max(n1r, n2r) - local_falloff)
        g = max(self.ambient, max(n1g, n2g) - local_falloff)
        b = max(self.ambient, max(n1b, n2b) - local_falloff)

        return (r, g, b)

    #figure out euclidean for propagation
    def forward_prop(self, map):
        for x in range(1, self.width):
            self.mask[self.idx(x,0)] = self.compute_intensity(self.mask[self.idx(x,0)],#here
                                                              self.mask[self.idx(x-1,0)],#neighbor1
                                                              (0.0, 0.0, 0.0), #neighbor2
                                                              self.opacity[self.idx(x,0)])#wall

        for y in range(1, self.height):
            self.mask[self.idx(0, y)] = self.compute_intensity(self.mask[self.idx(0, y)],
                                                               self.mask[self.idx(0, y-1)],
                                                               (0.0, 0.0, 0.0),
                                                               self.opacity[self.idx(0,y)])
            for x in range(1, self.width):
                self.mask[self.idx(x, y)] = self.compute_intensity(
                    self.mask[self.idx(x, y)],
                    self.mask[self.idx(x-1, y)],
                    self.mask[self.idx(x, y-1)],
                    self.opacity[self.idx(x,y)]
                )

    def backward_prop(self, map):
        for x in range(self.width-2, 0, -1):
            y = self.height - 1
            self.mask[self.idx(x, y)] = self.compute_intensity(self.mask[self.idx(x,y)],
                                                               self.mask[self.idx(x+1, y)],
                                                               (0.0, 0.0, 0.0),
                                                               self.opacity[self.idx(x,y)])

        for y in range(self.height-2, 0, -1):
            fx = self.width -1
            self.mask[self.idx(fx, y)] = self.compute_intensity(self.mask[self.idx(fx,y)],
                                                                self.mask[self.idx(fx, y+1)],
                                                                (0.0, 0.0, 0.0),
                                                                self.opacity[self.idx(fx,y)])

            for x in range(self.width-2, 0, -1):
                self.mask[self.idx(x, y)] = self.compute_intensity(
                    self.mask[self.idx(x, y)],
                    self.mask[self.idx(x+1, y)],
                    self.mask[self.idx(x, y+1)],
                    self.opacity[self.idx(x,y)]
                )

    def blur(self, _from, to, rad):
        numtiles = ((2 * rad) +1 ) * ((2 * rad)+1)
        for i in range(rad, self.width-rad):
            for j in range(rad, self.height-rad):
                sum = 0.0
                for x in range(i-rad, i+rad):
                    for y in range(j-rad, j+rad):
                        sum += _from[x+y*self.width]

                avg = sum/numtiles
                to[i+j*self.width] = avg

    def compute_mask(self, map):

        self.forward_prop(map)
        self.backward_prop(map)
        self.forward_prop(map)
        self.backward_prop(map)
        '''
        for x in range(self.width):
            for y in range(self.height):
                if map[x][y].opacity > 0.0:
                    if self.mask[self.idx(x,y)][0] > 0.0:
                        r = min(1.0, self.mask[self.idx(x,y)][0] +0.1)
                    if self.mask[self.idx(x,y)][1] > 0.0:
                        g = min(1.0, self.mask[self.idx(x,y)][1] +0.1)
                    if self.mask[self.idx(x, y)][2] > 0.0:
                        b = min(1.0, self.mask[self.idx(x,y)][2] +0.1)'''