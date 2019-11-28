__author__ = 'Grishnak'
import tcod as libtcod
from dungeon import dungeon
from dungeon import prefab_dungeon
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
class Level:
    def __init__(self):
        self.dungeon = None
        self.MAP_WIDTH = 0
        self.MAP_HEIGHT = 0
        self.fov_map = None

class DevMode:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.con = self.gEngine.console_new(self.gEngine.w, 48)
        # self.dungeon_gen = dungeon.BasicDungeon(48, self.gEngine.w, 10, 15, 15, 0, 0, self.gEngine)
        self.dungeon_gen = prefab_dungeon.PrefabGenerator(self.gEngine.w, 48, self.gEngine)
        #self.level = self.dungeon_gen.make_map()
        self.level = Level()
        self.level.dungeon = self.dungeon_gen.dungeon
        self.level.MAP_HEIGHT = 48
        self.level.MAP_WIDTH = self.gEngine.w

        self.gEngine.map_init_level(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        self.dungeon_gen.set_draw_map(self.level.dungeon)

        self.gEngine.map_init_level(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        self.level.fov_map = self.gEngine.get_fov_map()
        self.print_d_map = False
        self.active = True
        self.d = DijikstraMap(self.gEngine, self.gEngine.w, 48)
        c = [libtcod.yellow, libtcod.orange, libtcod.red, libtcod.purple]
        self.visualize_colors = libtcod.color_gen_map(c, [0, 12, 24, 36])
        self.m = None
        self.cx, self.cy = 0, 0
        self.v_map = None
        #self.gEngine.mMap = self.level.dungeon
        self.first = True
        self.level.dungeon = self.dungeon_gen.add_prefab_room(self.level.dungeon,
                                                              self.dungeon_gen.width,
                                                              self.dungeon_gen.height,
                                                              self.first)
    def run(self, key, mouse):
        while not libtcod.console_is_window_closed():
            self.gEngine.console_clear_all()
            key = libtcod.Key()
            mouse = libtcod.Mouse()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
            libtcod.map_compute_fov(self.level.fov_map, mouse.cx, mouse.cy)
            self.gEngine.lightmask_reset()

            self.testing(key, mouse)

            self.gEngine.lightmask_compute(self.level.dungeon)
            self.gEngine.map_draw(self.con, mouse.cx, mouse.cy, run_fov=False)
            #self.gEngine.map_draw_fast(self.con, mouse.cx, mouse.cy)

            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
            self.gEngine.console_flush()

        return True

    def testing(self, key, mouse):
        cx, cy = 0, 0
        self.gEngine.console_print(self.con, 1, 5, "(%dfps) Depth: %d" % (libtcod.sys_get_fps(), 1))
        if mouse.cx < self.level.MAP_WIDTH and mouse.cy < self.level.MAP_HEIGHT:
            self.gEngine.lightmask.add_light(mouse.cx, mouse.cy, 1.0)

        if key.vk == libtcod.KEY_SPACE:
            self.gEngine.map_clear()
            self.level.dungeon = self.dungeon_gen.add_prefab_room(self.level.dungeon,
                                                                  self.dungeon_gen.width,
                                                                  self.dungeon_gen.height,
                                                                  self.first)
            print(self.level.dungeon)
            self.dungeon_gen.set_draw_map(self.level.dungeon)
            self.level.fov_map = self.gEngine.get_fov_map()
            self.first = False

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
