__author__ = 'Grishnak'
import tcod as libtcod
from dungeon import dungeon


class DijikstraPoint:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value


class DijikstraMap:
    def __init__(self, gEngine, w, h):
        self.max_value = w * h
        self.map = [[self.max_value for x in range(h)] for y in range(w)]
        self.gEngine = gEngine
        self.w = w
        self.h = h
        self.points = []

    def compute(self, dungeon_map):
        while True:
            changes = False
            for x in range(self.w-2): # exclude the outside cells
                for y in range(self.h-2):
                    if not dungeon_map[x][y].blocked:
                        # check directions for lowest value to find the lowest value neighbor
                        valuex1 = self.map[x+1][y]
                        valuex_1 = self.map[x-1][y]
                        valuey1 = self.map[x][y+1]
                        valuey_1 = self.map[x][y-1]
                        valuexy1 = self.map[x+1][y+1]
                        valuexy_1 = self.map[x-1][y-1]
                        valueyx1 = self.map[x-1][y+1]
                        valueyx_1 = self.map[x+1][y-1]
                        value = min(valuex1, valuex_1, valuey1, valuey_1,
                                    valuexy1, valuexy_1, valueyx1, valueyx_1) # lowest value neighbor
                        dif = self.map[x][y] - value # get the difference between target tile and all neighbors
                        if dif > 1: # if the difference is greater than one, set target tile to 1 greater than neighbors
                            self.map[x][y] = value + 1
                            changes = True
            if changes is False:
                break

    def add_point(self, x, y, value):
        self.map[x][y] = value
        self.points.append(DijikstraPoint(x, y, value))

    def clear(self):
        self.map = [[self.max_value for x in range(self.h)] for y in range(self.w)]

    def remove_point(self,x, y):
        for point in self.points:
            if point.x == x and point.y == y:
                self.points.remove(point)
        self.clear()
        for point in self.points:
            self.map[point.x][point.y] = point.value


class DevMode:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.con = self.gEngine.console_new(self.gEngine.w, 48)
        self.dungeon_gen = dungeon.BasicDungeon(48, self.gEngine.w, 10, 15, 15, 0, 0, self.gEngine)
        self.level = self.dungeon_gen.make_map()
        self.print_d_map = False
        self.active = True
        self.d = DijikstraMap(self.gEngine, self.gEngine.w, 48)
        c = [libtcod.yellow, libtcod.orange, libtcod.red, libtcod.purple]
        self.visualize_colors = libtcod.color_gen_map(c, [0, 12, 24, 36])
    def run(self, key, mouse):
        while not libtcod.console_is_window_closed():
            self.gEngine.console_clear_all()
            key = libtcod.Key()
            mouse = libtcod.Mouse()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
            #libtcod.map_compute_fov(self.level.fov_map, mouse.cx, mouse.cy)
            #self.gEngine.lightmask_reset()

            self.testing(key, mouse)

            #self.gEngine.lightmask_compute(self.level.dungeon)
            self.gEngine.map_draw(self.con, mouse.cx, mouse.cy, run_fov=False)

            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
            self.gEngine.console_flush()

        return True

    def testing(self, key, mouse):
        if mouse.cx < self.level.MAP_WIDTH and mouse.cy < self.level.MAP_HEIGHT:
            self.gEngine.lightmask.add_light(mouse.cx, mouse.cy, 1.0)
        fr, fg, fb = libtcod.yellow
        br, bg, bb = libtcod.grey
        if key.vk == libtcod.KEY_SPACE:
            self.print_d_map = not self.print_d_map
        if mouse.lbutton:
            self.d.add_point(mouse.cx, mouse.cy, 0)
            self.d.compute(self.level.dungeon)
        if mouse.rbutton:
            self.d.remove_point(mouse.cx, mouse.cy)
            self.d.compute(self.level.dungeon)
        if self.print_d_map:
            for x in range(self.gEngine.w):
                for y in range(48):
                    h, s, v = self.gEngine.console_get_char_background(self.con, int(x), int(y))

                    if self.d.map[x][y] < 36:
                        col = self.visualize_colors[self.d.map[x][y]]
                    else:
                        if not self.gEngine.mMap[x +y * self.gEngine.w].blocked:
                            col = libtcod.grey
                        else:
                            col = libtcod.dark_grey
                        #libtcod.color_set_hsv(col, h, s, v)
                    br, bg, bb = col
                    self.gEngine.mMap[x +y * self.gEngine.w].color = col
                    c = ' '
                    c = self.d.map[x][y]

                    if c <= 9:
                        c = ord(str(c))
                    else:
                        c = ' '
                    self.gEngine.console_put_char_ex(self.con, x, y, c, fr, fg, fb, br, bg, bb)