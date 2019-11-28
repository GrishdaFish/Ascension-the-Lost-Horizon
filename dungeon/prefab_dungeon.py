__author__ = 'GrishdaFish'
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
from gEngine.utilities import xp_loader
import os
import sys
import tcod as libtcod
from copy import deepcopy
import time
width = 80
height = 43

if _gEngine.RELEASE:
    path = getattr(sys, "_MEIPASS", ".")
else:
    path = sys.path[0]
path = os.path.join(path, 'content')
path = path.replace('core.exe', '')


class PrefabGenerator:
    """
    Prefabricated map generator. Can be used as a standaone and build an entire level out of prefab rooms,
    can be used to generate a single prefabricated room in a map being  generated elsewhere,
    can load an entire level from a string.

    Will power scripted levels when scripting becomes available.
    """
    def __init__(self, w,  h, gEngine=None, game=None):
        self.game = game
        self.gEngine = gEngine
        self.width = w
        self.height = h
        self.dungeon = [[tile.Tile(True)
                         for y in range(self.height)]
                        for x in range(self.width)]
        self.room_holder = []

        self.load_prefab_rooms()

    def load_prefab_rooms(self):
        """
        Loads all of the prefab rooms from /content/prefabs/prefab_rooms for later use
        :return:
        """
        p = os.path.join(path, 'prefabs', 'prefab_rooms.txt')
        f = open(p)
        m = f.readlines()
        f.close()
        num_rooms = int(m.pop(0))  # pull the number of rooms out of the array and keep it
        room_size = 0
        offset = 0  # loop offset to find the length of the next room
        room_offset = 0  # offset for the start of the next room
        for i in range(num_rooms):
            room = []
            new_offset = int(m[i + offset])  # first, find the room size
            room_offset += 1  # offset past the number of room sizes, acts a sort of shift in the file
            for ii in range(room_offset, new_offset + room_offset):
                room.append(m[ii + offset].strip('\n'))
            offset = int(m[i + offset])  # change our offset to the next room's height value

            #convert array of strings, to 2d array to match layout
            h = []  # height array
            room_width = 0
            for r in room:
                w = []  # width array
                for c in r:
                    w.append(c)
                if len(w) > room_width:
                    room_width = len(w)  # find our widest room dimension
                h.append(w)
            room_height = len(h) # and get the height of our entire room
            self.room_holder.append((h, room_width, room_height))  # add a tuple with the room, plus it dimensions

    def add_prefab_room(self, map, width, height, first=False):
        """
        :param map: The map array to be worked on
        :param width: The width of the map
        :param height: The Height of the map
        :param first: Is this the first room generated on the map?
        :return: the worked on map
        """
        r = libtcod.random_get_int(0, 0, len(self.room_holder)-1)
        new_room = self.room_holder[r]  # grab a random room from the  list of rooms
        new_room_tiles = new_room[0]  # pull out relevant data
        new_room_width = new_room[1]
        new_room_height = new_room[2]
        trys = 8  # limit the number of trys so we don't waste too much time trying to place a room in a crowded map
        while trys > 0:
            # pick random room co-ords clamped to map dimensions, from room centerpoint
            room_x = libtcod.random_get_int(0, int(new_room_width + 1), int(width - new_room_width / 2 - 1))
            room_y = libtcod.random_get_int(0, int(new_room_height + 1), int(height - new_room_height / 2 - 1))
            failed = False

            # check to see if placing this room here would overlap another room or hallway
            for y in range(room_y - int(new_room_height / 2), room_y + int(new_room_height / 2)):
                if failed:
                    break
                for x in range(room_x - int(new_room_width / 2), room_x + int(new_room_width / 2)):
                    if not map[x][y].blocked:  # if we find one, we fail this try
                        failed = True
                        break
            if failed:
                trys -= 1
            else:  # if we find an open area large enough for this room, dig it o ut
                # loop through the room array
                for x in range(new_room_width-1):
                    for y in range(new_room_height-1):
                        if new_room_tiles[y][x] == '.':
                            # then place the room at the proper offsets from the center of the room
                            self.set_ground(x+room_x - int(new_room_width/2), y+room_y - int(new_room_height/2), map)
                break
        if not first:  # don't try to draw a hallway if this is the first room placed.
            pass  # draw hallways to the nearest connected room from a randomly chosen door
        return map

    def level_from_prefabs(self):
        pass

    def load_level_from_string(self, l, light_handler=None, colorset='town'):
        """
        Loads an entire level from a supplied string
        :param l: The level in string format to be loaded
        :param light_handler: the main light handler to place the levels pre placed lights
        :param colorset: the colorset to be used for this level, Defaults to town
        :return: Level() class with all relevant data populated for use
        TODO: When scripting is enabled, change the hardcoded values for floor, walls, npc, etc.. to script values
        """
        row = l.split('\n')
        h = []
        ground_color = [libtcod.desaturated_green]  # color_sets.colorset_town['ground']
        wall_color = [libtcod.light_grey]  # color_sets.colorset_town['wall']
        floor_color = color_sets.colorset_town['floor']
        noise = libtcod.noise_new(2)
        noise_zoom = 7.5
        noise_octaves = 1.9
        #print(cs)
        for r in row:
            w = []
            for c in r:
                w.append(c)
            h.append(w)
        dx, dy = 0, 0
        for y in range(self.height):
            for x in range(self.width):
                if colorset == 'town':
                    self.dungeon[x][y].explored = True
                if h[y][x] == ' ':
                    dx *= 1.25
                    dy *= 1.25
                    f = [noise_zoom * x / self.width + dx,
                         noise_zoom * y / self.width + dy]
                    value = libtcod.noise_get_fbm(noise, f, noise_octaves, libtcod.NOISE_PERLIN)
                    if value < 0:
                        value = -value
                    self.set_ground(x, y)
                    r = libtcod.random_get_int(0, 0, len(ground_color)-1)
                    r = deepcopy(ground_color[r])
                    # print(r)
                    r[0] += max(0, min(255, (r[0]*value)))
                    r[1] += max(0, min(255, (r[1]*value)))
                    r[2] += max(0, min(255, (r[2]*value)))
                    # print(r)
                    self.dungeon[x][y].color = r
                if h[y][x] == 'f':
                    self.set_ground(x, y)
                    r = libtcod.random_get_int(0, 0, len(floor_color)-1)
                    self.dungeon[x][y].color = floor_color[r]
                if h[y][x] == '#':
                    dx *= (dx * dx)
                    dy *= (dx * dx)
                    f = [-(noise_zoom * -x / self.width + dx),
                         (noise_zoom * -y / self.width + dy)]
                    value = libtcod.noise_get_fbm(noise, f, noise_octaves, libtcod.NOISE_PERLIN)
                    if value < 0:
                        value = -value

                    r = libtcod.random_get_int(0, 0, len(wall_color) - 1)
                    r = deepcopy(wall_color[r])
                    r[0] += max(0, min(255, (r[0] * value)))
                    r[1] += max(0, min(255, (r[1] * value)))
                    r[2] += max(0, min(255, (r[2] * value)))
                    self.dungeon[x][y].color = r

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
                    container.sort(key=lambda cons: cons.name)
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
                    for i in range(3):
                        item = self.game.build_objects.build_light_source(self.game, 0, 0)
                        container.append(item)

                    container.sort(key=lambda cons: cons.name)
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
                    container.sort(key=lambda cons: cons.name)
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
        # populate the level class with mandatory data
        if self.gEngine:
            self.gEngine.map_clear()
            self.set_draw_map(self.dungeon)
            fov_map = self.gEngine.get_fov_map()
            mmap = self.gEngine.get_map()
            if self.game:
                return level.Level(self.width, self.height, self.gEngine, self.dungeon, self.game.objects,
                                   fov_map=fov_map, draw_map=mmap)

    def load_room_from_xp(self, xp):
        """
        Loads a room from a RexPaint xp file
        :param xp: the xp file to load
        :return:
        """
        pass

    def set_draw_map(self, map):
        """
        Loads the generated map into the engine, and set light map opacity values, then inits the level FoV
        :param map: The map to be loaded into the engine
        :return: Nothing
        """
        for y in range(self.height):
            for x in range(self.width):
                c = map[x][y]
                self.gEngine.lightmask_set_opacity_value(x, y, c.opacity)
                self.gEngine.map_add_tile(x, y, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node, c.color,
                                          c.opacity)
        self.gEngine.map_init_level(self.width, self.height)

    def set_ground(self, x, y, map=None):
        """
        Sets the current tile to default walkable state
        :param x: X position of the tile
        :param y: Y position of the tile
        :param map: If supplied, the map to pull the  tile from, otherwise uses the class's dungeon
        :return: Nothing
        """
        x = int(x)
        y = int(y)
        if not map:
            self.dungeon[x][y].blocked = False
            self.dungeon[x][y].block_sight = False
            self.dungeon[x][y].tile = ' '#ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
            self.dungeon[x][y].opacity = 0.0
            self.dungeon[x][y].color = libtcod.Color(125, 125, 125)
        else:
            map[x][y].blocked = False
            map[x][y].block_sight = False
            map[x][y].tile = ' '  # ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
            map[x][y].opacity = 0.0
            map[x][y].color = libtcod.Color(125, 125, 125)
