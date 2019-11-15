__author__ = 'Grishnak'
import tcod as libtcod
from dungeon import dungeon
from gEngine.utilities.dijikstra_map import *
from copy import deepcopy

class FleeingAi:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y

    def calculate_move(self, d_map):
        current_cell = d_map[self.x][self.y]
        valid_options = None
        best_value = 100000
        # get the (x, y) values of all surrounding cells that has a value of 1 greater than current cell
        for x in range(self.x - 1, self.x + 2, 1):
            for y in range(self.y - 1, self.y + 2, 1):
                value = d_map[x][y]
                if value <= current_cell:
                    if value < best_value:
                        best_value = value
                        valid_options = (x, y)
        # pick a random cell from valid cells
        if valid_options:
            dest = valid_options
            self.x = dest[0]
            self.y = dest[1]
            return self.x, self.y
        else:
            return None, None



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
        self.m = None
        self.cx, self.cy = 0, 0
        self.v_map = None

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
        cx, cy = 0, 0
        if mouse.cx < self.level.MAP_WIDTH and mouse.cy < self.level.MAP_HEIGHT:
            self.gEngine.lightmask.add_light(mouse.cx, mouse.cy, 1.0)
        fr, fg, fb = libtcod.black
        br, bg, bb = libtcod.grey
        if key.vk == libtcod.KEY_SPACE:
            self.print_d_map = not self.print_d_map
        if mouse.lbutton_pressed:
            self.d.add_point(mouse.cx, mouse.cy, 0)
            self.d.compute(self.level.dungeon)
            self.v_map = deepcopy(self.d.map)
            self.d.multiply_map(-1.2, self.level.dungeon)
            self.d.compute(self.level.dungeon)

        if mouse.rbutton:
            self.d.remove_point(mouse.cx, mouse.cy)
            self.d.compute(self.level.dungeon)
            self.v_map = deepcopy(self.d.map)
        if mouse.mbutton_pressed:
            self.m = FleeingAi(mouse.cx, mouse.cy)
            for line in self.d.map:
                print(line)

        if key.vk == libtcod.KEY_ENTER:
            x, y = self.m.calculate_move(self.d.map)
            if x:
                self.cx, self.cy = x, y
        if self.print_d_map:
            for x in range(self.gEngine.w):
                for y in range(48):
                    h, s, v = self.gEngine.console_get_char_background(self.con, int(x), int(y))

                    if 36 > self.v_map[x][y] >= 0:
                        col = self.visualize_colors[self.v_map[x][y]]
                    else:
                        if not self.gEngine.mMap[x +y * self.gEngine.w].blocked:
                            col = libtcod.grey
                        else:
                            col = libtcod.dark_grey
                        #libtcod.color_set_hsv(col, h, s, v)
                    br, bg, bb = col
                    self.gEngine.mMap[x +y * self.gEngine.w].color = col
                    c = ' '
                    c = self.v_map[x][y]

                    if 9 >= c >= 0:
                        c = ord(str(c))
                    else:
                        c = ' '
                    self.gEngine.console_put_char_ex(self.con, x, y, c, fr, fg, fb, br, bg, bb)
        fr, fg, fb = libtcod.black
        self.gEngine.console_put_char_ex(self.con, self.cx, self.cy, 'x', fr, fg, fb, br, bg, bb)