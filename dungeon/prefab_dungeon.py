__author__ = 'GrishdaFish'
from dungeon import tile
from dungeon import level
from dungeon import rect
from dungeon import spawn_node

from dungeon.prefabs import color_sets

from game.user_interface import shop

from game.object import misc
from game.object import object as objects
from game.object import npc

from gEngine import lights

import os
import tcod as libtcod
from copy import deepcopy
import math
import random

width = 80
height = 43

path = os.path.abspath('.')
path = os.path.join(path, 'content')


# path = path.replace('core.exe', '')

door_options = [
    'door_1',
    'door_2',

]
class PrefabGenerator:
    """
    Prefabricated map generator. Can be used as a standaone and build an entire level out of prefab rooms,
    can be used to generate a single prefabricated room in a map being  generated elsewhere,
    can load an entire level from a string.

    Will power scripted levels when scripting becomes available.
    """

    def __init__(self, w, h, gEngine=None, game=None):
        self.game = game
        self.gEngine = gEngine
        self.gEngine.log_open_block("Initializing prefab generator")
        self.width = w
        self.height = h
        self.dungeon = [[tile.Tile(True)
                         for y in range(self.height)]
                        for x in range(self.width)]
        self.room_holder = []

        self.load_prefab_rooms()
        self.gEngine.log_message("Prefab generator initialized")
        self.gEngine.log_close_block()

    def load_prefab_rooms(self):
        """
        Loads all of the prefab rooms from /content/prefabs/prefab_rooms for later use
        :return:
        """
        p = os.path.join(path, 'prefabs', 'prefab_rooms.txt')
        self.gEngine.log_open_block("Loading prefabs from [%s]" % p)
        f = open(p)
        m = f.readlines()
        f.close()
        num_rooms = int(m.pop(0))  # pull the number of rooms out of the array and keep it
        self.gEngine.log_message("Loading [%d] rooms." % num_rooms)
        room_size = 0
        offset = 0  # loop offset to find the length of the next room
        room_offset = 0  # offset for the start of the next room
        for i in range(num_rooms):
            room = []
            new_offset = int(m[i + offset])  # first, find the room size
            room_offset += 1  # offset past the number of room sizes, acts a sort of shift in the file
            for ii in range(room_offset, new_offset + room_offset):
                room.append(m[ii + offset].strip('\n'))
            offset = offset + int(m[i + offset])  # change our offset to the next room's height value

            # convert array of strings, to 2d array to match layout
            h = []  # height array
            room_width = 0
            for r in room:
                w = []  # width array
                for c in r:
                    w.append(c)
                if len(w) > room_width:
                    room_width = len(w)  # find our widest room dimension
                h.append(w)
            room_height = len(h)  # and get the height of our entire room
            self.room_holder.append((h, room_width, room_height))  # add a tuple with the room, plus it dimensions
        self.gEngine.log_message("all rooms successfully loaded")
        self.gEngine.log_close_block()

    def add_prefab_room(self, map, width, height, first=False, rooms=None, connect_to_home=False, connect_to_closest=0,
                        max_path=25, place_over_hallways=False, light_handler=None, light_spawn_chance=100, max_trys=8):
        """
        Prefab room placement. Tries to plop in a prefabricated room into a map.
        Prefab room Legend:
        # = Wall
        . = Floor
        d = Door
        L = Wall + Light
        l = Floor + light (lowercase L)
        s = Monster Spawner (SpawnNode())
        :param map: The map array to be worked on
        :param width: The width of the map
        :param height: The Height of the map
        :param first: Is this the first room generated on the map?
        :param rooms: A list of rooms contained in this map
        :param connect_to_home: Force this room to connect to the first room generated
        :param connect_to_closest: Force this room to connect to the closest room as a secondary connection
        :param max_path: The longest a path hallway can be, before it triggers a mandatory secondary connection
        :param place_over_hallways: Can this room be placed over another hallway (but not a room) ?
        :param light_handler:  For generated lights to be placed in
        :param light_spawn_chance:  Chance to spawn pre placed room lights
        :param max_trys: The maximum number of attempts to place a room before failing
        :return: the worked on map, the list of rooms, and a spawn node

        """
        if not rooms:
            rooms = []
        r = libtcod.random_get_int(0, 0, len(self.room_holder) - 1)
        new_room = self.room_holder[r]  # grab a random room from the  list of rooms
        new_room_tiles = new_room[0]  # pull out relevant data
        new_room_width = new_room[1]
        new_room_height = new_room[2]
        center_x = int(new_room_width / 2)
        center_y = int(new_room_height / 2)
        room_x = 0
        room_y = 0
        doors = []  # to hold the positions of where we can make door and draw hallways from
        door_objects = []  # this will hold the actual door objects.
        trys = max_trys  # limit the number of trys so we don't waste time trying to place a room in a crowded map
        failed = False
        node_obj = None
        print("Finding room placement")
        while trys > 0:
            # pick random room co-ords clamped to map dimensions, from room center point
            if first:
                room_x = int(width / 2)
                room_y = int(height / 2)
            else:
                room_x = libtcod.random_get_int(0, int(new_room_width + 2), int(width - center_x - 2))
                room_y = libtcod.random_get_int(0, int(new_room_height + 2), int(height - center_y - 2))
                failed = False

                if place_over_hallways:
                    nroom = rect.Rect(room_x - center_x, room_y - center_y, new_room_width,
                                      new_room_height, doors, new_room_tiles)
                    for r in rooms:
                        if nroom.intersect(r):
                            failed = True
                            break
                else:
                    # check to see if placing this room here would overlap another room or hallway
                    for y in range(room_y - center_y - 1,
                                   room_y + center_y + 1):  # extend boundaries by 1 to leave a gap
                        if failed:
                            break  # as soon as we find a failure, break out of the loop to speed things along
                        for x in range(room_x - center_x - 1, room_x + center_x + 1):
                            if not map[x][y].blocked:  # if we find one, we fail this try
                                failed = True
                                break
            if failed:
                trys -= 1
            else:  # if we find an open area large enough for this room, dig it o ut
                # loop through the room array

                for x in range(new_room_width):
                    for y in range(new_room_height):
                        if new_room_tiles[y][x] == 'd':
                            doors.append((x + room_x - center_x, y + room_y - center_y))
                            #self.set_ground(x + room_x - center_x, y + room_y - center_y, map)

                        elif new_room_tiles[y][x] == '.':
                            # then place the room at the proper offsets from the center of the room
                            self.set_ground(x + room_x - center_x, y + room_y - center_y, map)
                        elif new_room_tiles[y][x] == 'L':
                            print("Found a wall light...")
                            if light_handler:
                                r = libtcod.random_get_int(0, 0, 100)
                                if r <= light_spawn_chance:
                                    print("...wall light added to light map")
                                    i = libtcod.random_get_float(0, 0.90, 1.15)
                                    l = lights.Light(x + room_x - center_x, y + room_y - center_y, light_handler,
                                                     flicker=True, intensity=i)
                                    light_handler.add_light(l)
                                    frames = ['wall_torch_a', 'wall_torch_b', 'wall_torch_c', 'wall_torch_d']
                                    random.shuffle(frames)
                                    self.gEngine.animation_add_cell_animation(self.game.dungeon_console, frames, True,
                                                                              x + room_x - center_x,
                                                                              y + room_y - center_y, delay=5, fore=False)
                        elif new_room_tiles[y][x] == 'l':
                            print("Found floor light...")
                            self.set_ground(x + room_x - center_x, y + room_y - center_y, map)
                            if light_handler:
                                r = libtcod.random_get_int(0, 0, 100)
                                if r <= light_spawn_chance:
                                    print("...floor light added")
                                    i = libtcod.random_get_float(0, 0.90, 1.15)#libtcod.random_get_float(0, 0.75, 1.0)
                                    l = lights.Light(x + room_x - center_x, y + room_y - center_y, light_handler,
                                                     flicker=True, intensity=i)
                                    light_handler.add_light(l)
                                    frames = ['wall_torch_a', 'wall_torch_b', 'wall_torch_c', 'wall_torch_d']
                                    random.shuffle(frames)
                                    self.gEngine.animation_add_cell_animation(self.game.dungeon_console, frames, True,
                                                                              x + room_x - center_x,
                                                                              y + room_y - center_y, delay=5,fore=False)

                        elif new_room_tiles[y][x] == 's':
                            self.set_ground(x + room_x - center_x, y + room_y - center_y, map)
                            if self.game:
                                map[x + room_x - center_x][y].spawn_node = True
                                node = spawn_node.SpawnNode(map[x + room_x - center_x][y + room_y - center_y],
                                                            x + room_x - center_x, y + room_y - center_y, self.game)
                                node_obj = objects.Object()
                                node_obj.node = node
                                node_obj.use = node.spawn_mobs
                                node_obj.node.owner = node_obj

                                # change this to append spawn nodes to level object
                                # then pass level object to ai_director
                                self.game.ai_director.spawn_nodes.append(node)
                                # node_obj.node.ticker.schedule_turn(0, node_obj)

                room = rect.Rect(room_x - center_x, room_y - center_y, new_room_width, new_room_height, doors,
                                 new_room_tiles)
                rooms.append(room)
                break  # break out of the loop if we draw a room to not waste time

        if trys == 0 and failed:  # if we ran out of trys and was unable to place a room
            print("Failed to place room")
            return False, rooms, node_obj  # room was unable to fit

        if not first:  # don't try to draw a hallway if this is the first room placed.
            # draw hallways to the nearest doorway from a randomly chosen door
            print("Room placed, generating tunnel")
            pmap = libtcod.map_new(width, height)  # create a new map for path finding to draw our new hallways

            print("setting map settings for pathing...")
            # set the walkable area to the entire map
            for y in range(height):
                for x in range(width):
                    libtcod.map_set_properties(pmap, x, y, True, True)
            for room in rooms:  # create a non walkable border around all rooms so we don't run halls next to rooms
                x1, x2, y1, y2 = room.outside_border()
                for y in range(y1, y2):
                    for x in range(x1, x2):
                        # self.set_ground(x, y, map)
                        libtcod.map_set_properties(pmap, x, y, False, False)

            dest_room = None
            if connect_to_home:  # should create a sort of spiral type map
                dest_room = rooms[0]
            else:
                r = libtcod.random_get_int(0, 0, len(rooms) - 2)  # get a room that isnt the new room
                dest_room = rooms[r]
            dest_doors = dest_room.doors
            origin_doors = rooms[len(rooms) - 1].doors  # will always be our newly created room

            # origin_door, dest_door = self.pick_doors(origin_doors, dest_doors)
            distance = 100000
            origin_door = []
            dest_door = []
            for odoor in origin_doors:
                for ddoor in dest_doors:
                    new_distance = self.door_distance_to(odoor, ddoor)
                    if new_distance < distance:
                        origin_door = odoor  # hodor????
                        dest_door = ddoor
                        distance = new_distance

            mat = self.game.build_objects.get_random_material()
            m = misc.Misc(type='door')
            d = door_options[libtcod.random_get_int(0, 0, len(door_options)-1)]
            door = objects.Object(self.game.dungeon_console, origin_door[0], origin_door[1], d, '%s door' % mat.name,
                                  libtcod.white, blocks=True, misc=m)
            door.game = self.game
            m.attach_owner(door)
            m.set_use_function(m.open)
            door.misc.setup_popups()
            self.game.objects.append(door)

            self.set_ground(origin_door[0], origin_door[1], map)
            libtcod.map_set_properties(pmap, origin_door[0], origin_door[1], True, True)
            self.set_ground(dest_door[0], dest_door[1], map)
            libtcod.map_set_properties(pmap, dest_door[0], dest_door[1], True, True)

            wpath = libtcod.path_new_using_map(pmap, 0)  # we set the diagonal cost to 0 to avoid using diags for halls

            # loop through the path to create the hallway to the target room
            libtcod.path_compute(wpath, origin_door[0], origin_door[1], dest_door[0], dest_door[1])
            if libtcod.path_size(wpath) > max_path:
                connect_to_closest = 100  # if a path is too long, force a connection to the closest room
            print("Walking path....")
            for i in range(libtcod.path_size(wpath)):
                x, y = libtcod.path_get(wpath, i)
                if not map[x][y].blocked:  # if we find our next step is a walkable tile, stop the hallway
                    print("Ran into another blank space, ending pathing!")
                    self.set_ground(x, y, map)
                    # set the dest door to a wall so it doesnt look out of place since we wont path to it
                    # self.set_wall(dest_door[0], dest_door[1], map)
                    break
                self.set_ground(x, y, map)

            print('Pathing complete')

            r = libtcod.random_get_int(0, 0, 100)
            if r <= connect_to_closest:
                origin_doors = []
                dest_doors = []
                print("Generating secondary connection...")
                origin_room = rooms[len(rooms) - 1]
                distance = 100000000
                dest_room = None
                for room in rooms:
                    new_distance = self.room_distance_to(origin_room, room)
                    # print(new_distance)
                    if new_distance != 0.0:
                        if new_distance < distance:
                            distance = new_distance
                            dest_room = room
                origin_doors = origin_room.doors
                dest_doors = dest_room.doors
                distance = 100000
                origin_door = []
                dest_door = []
                for odoor in origin_doors:
                    for ddoor in dest_doors:
                        new_distance = self.door_distance_to(odoor, ddoor)
                        # print(new_distance)
                        if new_distance < distance:
                            origin_door = odoor  # hodor????
                            dest_door = ddoor
                            distance = new_distance

                self.set_ground(origin_door[0], origin_door[1], map)
                libtcod.map_set_properties(pmap, origin_door[0], origin_door[1], True, True)
                self.set_ground(dest_door[0], dest_door[1], map)
                libtcod.map_set_properties(pmap, dest_door[0], dest_door[1], True, True)

                wpath = libtcod.path_new_using_map(pmap, 0)
                libtcod.path_compute(wpath, origin_door[0], origin_door[1], dest_door[0], dest_door[1])
                print("Walking secondary path....")
                for i in range(libtcod.path_size(wpath)):
                    x, y = libtcod.path_get(wpath, i)
                    self.set_ground(x, y, map)
                print('Secondary pathing complete')

            print("Checking to see if room is connected...")
            for y in range(height):
                for x in range(width):
                    if not map[x][y].blocked:
                        libtcod.map_set_properties(pmap, x, y, True, True)
            wpath = libtcod.path_new_using_map(pmap, 0)
            this_room = rooms[len(rooms) - 1]
            home_room = rooms[0]
            this_cx, this_cy = this_room.center()

            if map[this_cx][this_cy].blocked:
                print("This_room center is not walkable, finding first walkable tile in room...")
                x1, x2, y1, y2 = this_room.outside_border()
                found = False
                for y in range(y1, y2):
                    if found:
                        break
                    for x in range(x1, x2):
                        if not map[x][y].blocked:
                            this_cx = x
                            this_cy = y
                            found = True
                            print("..found walkable tile.")
                            break

            home_cx, home_cy = home_room.center()
            if map[home_cx][home_cy].blocked:
                print("Home_room center is not walkable, finding first walkable tile in room...")
                x1, x2, y1, y2 = home_room.outside_border()
                found = False
                for y in range(y1, y2):
                    if found:
                        break
                    for x in range(x1, x2):
                        if not map[x][y].blocked:
                            home_cx = x
                            home_cy = y
                            found = True
                            print("..found walkable tile.")
                            break

            if not libtcod.path_compute(wpath, this_cx, this_cy, home_cx, home_cy):
                print('Room is not connected...')
                x1, x2, y1, y2 = this_room.outside_border()
                print('Covering up room...')
                for y in range(y1, y2):
                    for x in range(x1, x2):
                        self.set_wall(x, y, map)
                print('...Done. Removing room from list...')
                rooms.remove(this_room)
                print('...Done. Room addition failed due to lack of proper connection. Returning...')
            else:
                print('Room is connected')
                print("Room addition completed!")
        else:
            print("First room set!")
        return map, rooms, node_obj  # , door_objects

    def pick_doors(self, dest_doors, origin_doors):  # this bugs the generator out for some reason *shrugs*
        """
        Returns the pair of closest doors from a list of doors
        :param dest_doors:
        :param origin_doors:
        :return:
        """
        distance = 100000
        origin_door = []
        dest_door = []
        for odoor in origin_doors:
            for ddoor in dest_doors:
                new_distance = self.door_distance_to(odoor, ddoor)
                if new_distance < distance:
                    origin_door = odoor  # hodor????
                    dest_door = ddoor
                    distance = new_distance
        return (origin_door, dest_door)

    def level_from_prefabs(self, max_rooms=15, max_trys=50, max_room_items=3, max_level_items=15,
                           light_handler=None, light_spawn_chance=70):
        self.dungeon = [[tile.Tile(True)
                         for y in range(self.height)]
                        for x in range(self.width)]
        map_rooms = []
        spawn_nodes = []
        doors = []
        first = True

        for r in range(max_rooms):
            dungeon, rooms, s = self.add_prefab_room(self.dungeon, self.width, self.height, first=first,
                                                     rooms=map_rooms, connect_to_home=False, connect_to_closest=50,
                                                     max_path=30, place_over_hallways=True,
                                                     light_handler=light_handler,
                                                     light_spawn_chance=light_spawn_chance, max_trys=max_trys)
            first = False
            if dungeon:
                self.dungeon = dungeon
            map_rooms = rooms
            if s:
                spawn_nodes.append(s)
            # if d:
            #    doors.append(d)
        down = False
        if self.game:
            while not down:
                x = libtcod.random_get_int(0, 0, self.width - 1)
                y = libtcod.random_get_int(0, 0, self.height - 1)
                if not self.dungeon[x][y].blocked:
                    m = misc.Misc(type='down')
                    down = objects.Object(self.game.dungeon_console, x, y, 'stairs_down', 'set of stairs going down',
                                          libtcod.white, blocks=False, misc=m)
                    self.game.objects.append(down)
                    down.send_to_back(self.game.objects)
                    down = True
            up = False
            while not up:
                x = libtcod.random_get_int(0, 0, self.width - 1)
                y = libtcod.random_get_int(0, 0, self.height - 1)
                if not self.dungeon[x][y].blocked:
                    m = misc.Misc(type='up')
                    up = objects.Object(self.game.dungeon_console, x, y, 'stairs_up', 'set of stairs going up',
                                        libtcod.white, blocks=False, misc=m)
                    self.game.objects.append(up)
                    up.send_to_back(self.game.objects)
                    up = True
            for room in map_rooms:
                max_level_items = self.spawn_ground_items(room, min(max_room_items, max_level_items), max_level_items)
                if max_level_items <= 0:
                    break
            for object in self.game.objects:
                object.message = self.game.message
                object.objects = self.game.objects

        self.gEngine.map_new(self.width, self.height)
        self.gEngine.map_clear()
        self.set_draw_map(self.dungeon)
        fov_map = self.gEngine.get_fov_map()
        mmap = self.gEngine.get_map()
        print(map_rooms)

        for obj in self.game.objects:
            if obj.misc:
                if obj.misc.type == "door":
                    pass
                    self.gEngine.map_change_tile_blocking(obj.x, obj.y, True, True)
        if self.game:
            return level.Level(self.width, self.height, self.gEngine, self.dungeon, self.game.objects, self.game.depth,
                               fov_map=fov_map, draw_map=mmap, rooms=map_rooms)
        else:
            return level.Level(self.width, self.height, self.gEngine, self.dungeon, fov_map=fov_map, draw_map=mmap,
                               rooms=map_rooms)

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
        # print(cs)
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
                    r = libtcod.random_get_int(0, 0, len(ground_color) - 1)
                    r = deepcopy(ground_color[r])
                    # print(r)
                    # r[0] += max(0, min(255, (r[0]*value)))
                    # r[1] += max(0, min(255, (r[1]*value)))
                    # r[2] += max(0, min(255, (r[2]*value)))
                    # print(r)
                    self.dungeon[x][y].color = r
                if h[y][x] == 'f':
                    self.set_ground(x, y)
                    r = libtcod.random_get_int(0, 0, len(floor_color) - 1)
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
                    down = objects.Object(self.game.dungeon_console, x, y, 'stairs_down', 'set of stairs going down',
                                          libtcod.white,
                                          blocks=False, misc=m)
                    self.game.objects.append(down)
                    down.send_to_back(self.game.objects)
                # check for NPC locations
                if h[y][x] == 'W':
                    img = os.path.join(path, 'img', 'bg-wep.png')
                    container = []
                    for i in range(10):  ##Need to init objects and message in object creation
                        item = self.game.ai_director.get_equipment(0, 0, 'melee')
                        container.append(item)
                    container.sort(key=lambda cons: cons.name)
                    n = npc.NPC()
                    n.attach_shop("Johan's Weaporium", img, container, shop.shop)
                    n = objects.Object(self.game.dungeon_console, x, y, '@', 'Johan', libtcod.white, blocks=True, npc=n)
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
                    n = objects.Object(self.game.dungeon_console, x, y, '@', 'Fizzilip', libtcod.white, blocks=True,
                                       npc=n)
                    self.game.objects.append(n)
                    self.set_ground(x, y)
                if h[y][x] == 'Q':
                    self.set_ground(x, y)
                if h[y][x] == 'A':
                    img = os.path.join(path, 'img', 'bg-arm.png')
                    container = []
                    for i in range(10):  ##Need to init objects and message in object creation
                        item = self.game.ai_director.get_equipment(0, 0, 'armor')
                        container.append(item)
                    container.sort(key=lambda cons: cons.name)
                    n = npc.NPC()
                    n.attach_shop("The Helm and Buckler", img, container, shop.shop)
                    n = objects.Object(self.game.dungeon_console, x, y, '@', 'Garrius', libtcod.white, blocks=True,
                                       npc=n)
                    self.game.objects.append(n)
                    self.set_ground(x, y)
                # check for light locations
                if h[y][x] == "L":
                    self.set_ground(x, y)
                    i = libtcod.random_get_float(0, 0.9, 1.25)#libtcod.random_get_float(0, 0.85, 1.0)
                    if light_handler:
                        l = lights.Light(x, y, light_handler,  flicker=True, intensity=i)
                        light_handler.add_light(l)
                        frames = ['wall_torch_a', 'wall_torch_b', 'wall_torch_c', 'wall_torch_d']
                        random.shuffle(frames)
                        self.gEngine.animation_add_cell_animation(self.game.dungeon_console, frames, True, x, y,
                                                                  delay=5, fore=False)
                # player starting location
                if h[y][x] == 'X':
                    self.set_ground(x, y)
                    self.game.player.x = x
                    self.game.player.y = y
        # populate the level class with mandatory data
        if self.gEngine:
            self.gEngine.map_new(self.width, self.height)
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

    def spawn_ground_items(self, room, max_room_items, max_level_items):
        num_items = libtcod.random_get_int(0, 0, max_room_items)
        types = {0: self.game.build_objects.build_light_source,
                 1: self.game.build_objects.build_potion,
                 2: self.game.build_objects.build_scroll,
                 }
        for i in range(num_items):
            # choose random spot for this item
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
            t = libtcod.random_get_int(0, 0, len(types) - 1)
            # only place it if the tile is not blocked
            if not self.dungeon[x][y].blocked:
                self.game.objects.append(types[t](self.game, x, y))
        return max_level_items - num_items

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
            self.dungeon[x][y].tile = ' '  # ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
            self.dungeon[x][y].opacity = 0.0
            self.dungeon[x][y].color = libtcod.Color(125, 125, 125)
        else:
            map[x][y].blocked = False
            map[x][y].block_sight = False
            map[x][y].tile = ' '  # ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
            map[x][y].opacity = 0.0
            map[x][y].color = libtcod.Color(125, 125, 125)

    def set_wall(self, x, y, map=None):
        x = int(x)
        y = int(y)
        if not map:
            self.dungeon[x][y].blocked = False
            self.dungeon[x][y].block_sight = False
            self.dungeon[x][y].tile = ' '  # ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
            self.dungeon[x][y].opacity = 0.0
            self.dungeon[x][y].color = libtcod.Color(99, 99, 99)
        else:
            map[x][y].blocked = True
            map[x][y].block_sight = True
            map[x][y].tile = '#'  # ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
            map[x][y].opacity = 1.0
            map[x][y].color = libtcod.Color(99, 99, 99)

    def door_distance_to(self, door1, door2):
        dx = door2[0] - door1[0]
        dy = door2[1] - door1[1]
        v = (dx ** 2) + (dy ** 2)
        return math.sqrt((int(v)))

    def room_distance_to(self, room1, room2):
        x2, y2 = room2.center()
        x1, y1 = room1.center()
        dx = x2 - x1
        dy = y2 - y1
        v = (dx ** 2) + (dy ** 2)
        return math.sqrt((int(v)))
