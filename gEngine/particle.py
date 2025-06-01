__author__ = 'Grishnak'
import math
import tcod as libtcod
import time


# TODO: Add additional Particle array for character particles

def explosion(num_particles, particle_array, x, y, decay=0.055, random_decay=True, bounce=True, color=None, velocity=1.0, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
    for i in range(num_particles):
        particle_array.append(Particle(x, y, decay=decay, velocity=velocity, random_decay=random_decay, bounce=bounce, color=color, lifetime=lifetime, clipping=clipping, char=char, kill_no_vel=kill_no_vel))


def nova(num_particles, particle_array, x, y, random_decay=False, bounce=False, color=None, velocity=1.0, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
    increment = (num_particles) / 3.14159
    angle = math.atan2(float(-y), float(-x))
    for i in range(num_particles / 2):
        angle = i + increment
        particle_array.append(Particle(x, y, 0.1, 1.0, angle, random_decay, bounce, clipping=clipping, char=char, kill_no_vel=kill_no_vel))
    for i in range(num_particles / 2):
        angle = i - increment
        particle_array.append(Particle(x, y, 0.1, 1.0, -angle, random_decay, bounce, clipping=clipping, char=char, kill_no_vel=kill_no_vel))


def cone_spray(num_particles, particle_array, ox, oy, dx, dy, random_decay=False, bounce=False, color=None, velocity=1.0, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))
    for i in range(num_particles):
        angle2 = angle + libtcod.random_get_float(0, -0.25, 0.25)
        velocity = 1.0 + libtcod.random_get_float(0, -0.05, 0.05)
        decay = 0.09 + libtcod.random_get_float(0, -0.05, 0.05)
        particle_array.append(Particle(ox, oy, decay, velocity, angle2, random_decay, bounce, clipping=clipping, char=char, kill_no_vel=kill_no_vel))


def cone(num_particles, particle_array, ox, oy, dx, dy, random_decay=False, bounce=False, color=None, velocity=1.0, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))
    for i in range(num_particles):
        angle2 = angle + libtcod.random_get_float(0, -0.25, 0.25)
        velocity = 1.0
        decay = 0.1
        particle_array.append(Particle(ox, oy, decay, velocity, angle2, random_decay, bounce, color, lifetime, clipping=clipping, char=char, kill_no_vel=kill_no_vel))


def projectile(num_particles, particle_array, ox, oy, dx, dy, random_decay=False, bounce=False, color=None, velocity=1.0, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))
    particle_array.append(Particle(ox, oy, 0.05, velocity, angle, random_decay, bounce, color, lifetime, clipping=clipping, char=char, kill_no_vel=kill_no_vel))


def uniform_intensity_burst(color):
    factor = 3.0
    clamp = 1.5
    # generate a random number with a combined light intensity of 3.0 (brighter than any standard light)
    if not color:
        r = libtcod.random_get_float(0, 0.1, 1.5)
        g = libtcod.random_get_float(0, 0.1, 1.5)
        b = libtcod.random_get_float(0, 0.1, 1.5)
    else:
        r = color[0] / 255
        g = color[1] / 255
        b = color[2] / 255

    # add them all together, then divide them by our target intensity
    s = r + g + b
    f = factor / s

    # then multiply the originally generated numbers by the factor to get target intensity
    r = min(clamp, r * f)  # but clamp to 1.5 intensity to prevent washout of a single color being too bright
    g = min(clamp, g * f)
    b = min(clamp, b * f)

    # get sum again (to maintain overall intensity, likely isnt completely accurate,
    # but it is close enough to the intention
    s = r + g + b
    f = factor / s
    if s < factor:
        if r == clamp:
            g = g * f
            b = b * f
        elif g == clamp:
            r = r * f
            b = b * f
        else:
            r = r * f
            g = g * f

    return (r, g, b)


class Particle:
    def __init__(self, x, y, decay=0.1, velocity=1.0, angle=None, random_decay=True, bounce=False, color=None, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
        self.x = x
        self.y = y
        self.decay = decay
        self.can_bounce = bounce
        self.lifetime = lifetime
        self.max_lifetime = time.time()
        self.color_dict = None
        self.clipping = clipping
        self.kill_no_vel=kill_no_vel
        if char:
            if isinstance(char, list):
                i = libtcod.random_get_int(0,0, len(char)-1)
                self.char = char[i]
            elif isinstance(char, tuple):
                i = libtcod.random_get_int(0, 0, len(char) - 1)
                self.char = char[i]
            else:
                self.char = char
        else:
            self.char = None

        if random_decay:
            self.decay += libtcod.random_get_float(0, -0.05, 0.05)
        if self.decay <= 0:
            self.decay = 0.05
        self.velocity = velocity
        self.dead = False
        if angle is None:
            self.angle = math.atan2(float(-y), float(-x))
            self.angle += libtcod.random_get_float(0, -3.14159, 3.14159)
        else:
            self.angle = angle
        self.dir_x = math.cos(self.angle * self.velocity)
        self.dir_y = math.sin(self.angle * self.velocity)
        # print(self.color)
        if color:
            self.color = color # color[0]
            """if len(color) == 1:
                self.color = color[0]  # uniform_intensity_burst(color)
            elif len(color) > 1:
                color_breakpoint = int(100/len(color))
                percentage_list = []
                counter = -1
                self.color_dict = {}
                for x in range(len(color)):
                    c = (counter+2, counter+color_breakpoint+1)
                    counter += color_breakpoint
                    percentage_list.append(c)
                for x in range(len(color)):
                    self.color_dict[percentage_list[x]] = color[x]

                self.color = self.color_dict[percentage_list[0]]
            else:
                self.color = libtcod.white  # uniform_intensity_burst(color)"""
        else:
            self.color = libtcod.white

    def update(self, gEngine):
        if self.dead:
            return

        newx = self.x + self.dir_x * self.velocity
        newy = self.y + self.dir_y * self.velocity

        if (time.time() - self.max_lifetime) > self.lifetime:
            self.dead = True
            return

        if gEngine:
            if self.clipping:
                collide = not gEngine.engine.mDungeonIsWalkable(int(newx), int(newy))  # map[int(newx)][int(newy)].blocked
                if collide:
                    if self.can_bounce:
                        # determine angle of bounce with black magic
                        cdx = int(newx - self.x) / 2
                        cdy = int(newy - self.y) / 2

                        if cdx == 0:
                            self.dir_y = (-self.dir_y)
                        if cdy == 0:
                            self.dir_x = (-self.dir_x)
                        else:
                            self.dead = True
                        #    return
                    else:
                        self.dead = True
                        return
            value = (time.time() - self.max_lifetime) / self.lifetime
            if value == 0:
                value = 0.1
            value = 100/value
            if self.color_dict:
                for key_range, val in self.color_dict.items():
                    if value >= key_range[0] and value <= key_range[1]:
                        self.color = val

            self.x = newx
            self.y = newy
            self.velocity -= self.decay
            if self.velocity < 0:
                self.velocity = 0
                if self.kill_no_vel:
                    self.dead = True

            # self.lifetime -= self.decay
            # light = (self.color[0], self.color[1], self.color[2], 2.5)
            # if lightmask:
            #     lightmask.add_light(int(self.x), int(self.y), self.color)

    def draw(self, gEngine, con):  # change this to lightmap drawing once subcell res is implemented
        if self.char:
            x = self.x/2
            y = self.y/2
            col = gEngine.get_map_tile_color(int(x), int(y))
            brightness = gEngine.lightmask_get_mask_value(x, y)
            fr, fg, fb = self.color
            br, bg, bb = col
            br *= brightness[0]
            bg *= brightness[1]
            bb *= brightness[2]
            br = min(255, br)
            bg = min(255, bg)
            bb = min(255, bb)

            gEngine.console_put_char_ex(con, int(x), int(y), self.char, (fr, fg, fb),
                                        (int(br), int(bg), int(bb)))  # self.char,self.color,col)
        else:
            gEngine.image_put_pixel(-1, int(self.x), int(self.y), (int(self.color[0]), int(self.color[1]), int(self.color[2])))

    def get_angle(self, dx, dy):
        self.angle = math.atan2(float(dy), float(dx))
        return self.angle

    def get_color(self):
        x = libtcod.Color()

if __name__ == "__main__":
    l = [1, 2, 3, 4, 5]
    p = int(100/len(l))
    print(p)
    p_list = []
    counter = -1
    for x in range(len(l)):
        c = (counter+2, counter+p+1)
        counter += p
        p_list.append(c)
    print(p_list)
    d = {}
    for x in range(len(l)):
        d[p_list[x]] = l[x]

    print(d)
    value = 36
    for key_range, val in d.items():
        if value >= key_range[0] and value <= key_range[1]:
            print(val)
    print(type(libtcod.Color))

    lifetime =  1.5
    max_lifetime = time.time()# + lifetime
    print(max_lifetime)
    while True:
        print(time.time() - max_lifetime)
        if (time.time() - max_lifetime) > lifetime:
            print(max_lifetime)
            break
