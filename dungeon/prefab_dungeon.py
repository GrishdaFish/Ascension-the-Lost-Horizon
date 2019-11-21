__author__ = 'Grishnak'
from dungeon import tile
from dungeon import level
from dungeon import spawn_node
from dungeon.prefabs import prefabs
from dungeon.prefabs import color_sets
from game.user_interface import shop
from game.object import misc
from game.object import object
from game.object import npc
from gEngine import lights
from gEngine import gEngine as _gEngine
import os
import sys
import tcod as libtcod

width = 80
height = 43



class PrefabGenerator:
    def __init__(self, w,  h, gEngine=None, game=None):
        self.game = game
        self.gEngine = gEngine
        self.width = w
        self.height = h
        self.dungeon = [[tile.Tile(True)
                         for y in range(self.height)]
                        for x in range(self.width)]

    def load_level_from_string(self, l, light_handler=None, colorset='town'):
        row = l.split('\n')
        h = []
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        path = os.path.join(path, 'content')
        path = path.replace('core.exe', '')

        ground_color = color_sets.colorset_town['ground']
        wall_color = color_sets.colorset_town['wall']
        floor_color = color_sets.colorset_town['floor']
        #print(cs)
        for r in row:
            w = []
            for c in r:
                w.append(c)
            h.append(w)

        for y in range(self.height):
            for x in range(self.width):
                if colorset == 'town':
                    self.dungeon[x][y].explored = True
                if h[y][x] == ' ':
                    self.set_ground(x, y)
                    r = libtcod.random_get_int(0, 0, len(ground_color)-1)
                    self.dungeon[x][y].color = ground_color[r]
                if h[y][x] == 'f':
                    self.set_ground(x, y)
                    r = libtcod.random_get_int(0, 0, len(floor_color)-1)
                    self.dungeon[x][y].color = floor_color[r]
                if h[y][x] == '#':
                    r = libtcod.random_get_int(0, 0, len(wall_color) - 1)
                    self.dungeon[x][y].color = wall_color[r]

                # check for doors
                # check for stairs
                if h[y][x] == '>':
                    self.set_ground(x, y)
                    r = libtcod.random_get_int(0, 0, len(floor_color) - 1)
                    self.dungeon[x][y].color = floor_color[r]
                    m = misc.Misc(type='down')
                    down = object.Object(self.game.dungeon_console, x, y, '>', 'set of stairs going down', libtcod.white,
                                  blocks=False, misc=m)
                    self.game.objects.append(down)
                    down.send_to_back(self.game.objects)
                # check for NPC locations
                if h[y][x] == 'W':
                    img = os.path.join(path, 'img', 'bg-wep.png')
                    container = []
                    for i in range(10):  ##Need to init objects and message in object creation
                        item = self.game.build_objects.build_equipment(self.game, 0, 0, 'melee')
                        container.append(item)
                    n = npc.NPC()
                    n.attach_shop("Johan's Weaporium", img, container, shop.shop)
                    n = object.Object(self.game.dungeon_console, x, y, '@', 'Johan', libtcod.white, blocks=True, npc=n)
                    self.game.objects.append(n)
                    self.set_ground(x, y)
                if h[y][x] == 'M':
                    img = os.path.join(path, 'img', 'bg-magic.png')
                    container = []
                    for i in range(10):  ##Need to init objects and message in object creation
                        item = self.game.build_objects.build_potion(self.game, 0, 0)
                        container.append(item)
                        item = self.game.build_objects.build_scroll(self.game, 0, 0)
                        container.append(item)
                    n = npc.NPC()
                    n.attach_shop("Fizzilip's Magiteria", img, container, shop.shop)
                    n = object.Object(self.game.dungeon_console, x, y, '@', 'Fizzilip', libtcod.white, blocks=True, npc=n)
                    self.game.objects.append(n)
                    self.set_ground(x, y)
                if h[y][x] == 'Q':
                    self.set_ground(x, y)
                if h[y][x] == 'A':
                    img = os.path.join(path, 'img', 'bg-arm.png')
                    container = []
                    for i in range(10):  ##Need to init objects and message in object creation
                        item = self.game.build_objects.build_equipment(self.game, 0, 0, 'armor')
                        container.append(item)
                    n = npc.NPC()
                    n.attach_shop("The Helm and Buckler", img, container, shop.shop)
                    n = object.Object(self.game.dungeon_console, x, y, '@', 'Garrius', libtcod.white, blocks=True, npc=n)
                    self.game.objects.append(n)
                    self.set_ground(x, y)
                # check for light locations
                if h[y][x] == "L":
                    self.set_ground(x, y)
                    i = libtcod.random_get_float(0, 0.85, 1.0)
                    if light_handler:
                        l = lights.Light(x, y, light_handler, color=libtcod.white, flicker=True, intensity=i)
                        light_handler.add_light(l)
                # player starting location
                if h[y][x] == 'X':
                    self.set_ground(x, y)
                    self.game.player.x = x
                    self.game.player.y = y
        if self.gEngine:
            self.gEngine.map_clear()
            self.set_draw_map(self.dungeon)
            fov_map = self.gEngine.get_fov_map()
            mmap = self.gEngine.get_map()
            if self.game:
                return level.Level(self.width, self.height, self.gEngine, self.dungeon, self.game.objects,
                                   fov_map=fov_map, draw_map=mmap)
    def set_draw_map(self, map):
        for y in range(self.height):
            for x in range(self.width):
                c = map[x][y]
                self.gEngine.lightmask_set_opacity_value(x, y, c.opacity)
                self.gEngine.map_add_tile(x, y, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node, c.color,
                                          c.opacity)
        self.gEngine.map_init_level(self.width, self.height)

    def set_ground(self, x, y):
        x = int(x)
        y = int(y)
        self.dungeon[x][y].blocked = False
        self.dungeon[x][y].block_sight = False
        self.dungeon[x][y].tile = ' '#ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
        self.dungeon[x][y].opacity = 0.0
        self.dungeon[x][y].color = libtcod.Color(125, 125, 125)

if __name__ == "__main__":
    import tile
    p = PrefabGenerator()
    p.load_level_from_string(town)
