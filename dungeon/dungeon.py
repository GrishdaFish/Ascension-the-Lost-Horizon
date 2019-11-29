__author__ = 'GrishdaFish'
from dungeon.rect import Rect
from dungeon.tile import Tile
from dungeon.level import Level
from dungeon.spawn_node import SpawnNode
from game.object.misc import *
from game.object.object import *
from gEngine import lights

MAX_DEPTH = 25
# Variables for tile bitmasking
tile_bitshift = 4
tile_bit_offset = 31

ground_tiles = [',', '.', "'", '`']


def idx(x, y, w):
    return x + y * w



# TODO get rid of 2d arrays, and  use 1d array + idx(x, y, w)


class BasicDungeon:
    def __init__(self, mh, mw, rmin, rmax, r, rm, ri, gEngine, logger=None):
        self.MAP_HEIGHT = mh
        self.MAP_WIDTH = mw
        self.ROOM_MIN_SIZE = rmin
        self.ROOM_MAX_SIZE = rmax
        self.MAX_ROOMS = r
        self.MAX_ROOM_MONSTERS = rm
        self.MAX_ROOM_ITEMS = ri
        self.logger = logger
        self.depth = 0
        self.map = None
        self.spawn_nodes = None
        self.map2x = None
        self.gEngine = gEngine

    def set_ground(self, x, y):
        x = int(x)
        y = int(y)
        self.map[x][y].blocked = False
        self.map[x][y].block_sight = False
        self.map[x][y].tile = ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
        self.map[x][y].opacity = 0.0
        self.map[x][y].color = libtcod.Color(125, 125, 125)

    def create_room(self, room, game=None, random_instance=None):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.set_ground(x, y)
        while 1:
            x = libtcod.random_get_int(random_instance, room.x1 - 1, room.x2 - 1)
            y = libtcod.random_get_int(random_instance, room.y1 - 1, room.y2 - 1)
            # only place it if the tile is not blocked
            if not self.is_blocked(x, y, game):
                break
        if game:
            self.create_spawn_node(x, y, game)

    def create_h_tunnel(self, x1, x2, y):
        # horizontal tunnel. min() and max() are used in case x1>x2
        for x in range(int(min(x1, x2)), int(max(x1, x2)) + 1):
            self.set_ground(x, y)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(int(min(y1, y2)), int(max(y1, y2)) + 1):
            self.set_ground(x, y)

    def return_bitmask_map(self, map=None, width=None, height=None):
        # returns a 1d array with the bitmasks of each tile
        if not width:
            width = self.MAP_WIDTH
        if not height:
            height = self.MAP_HEIGHT
        if not map:
            map = self.map

        bit_map_arr = []
        for x in range(width):
            for y in range(height):
                bit_map_arr.append(map[x][y].return_bitmask())
        return bit_map_arr

    def build_bitmask_map(self, bitmask_map, game):
        # build a map from a bitmask array
        # tiles[y*10+x]
        map = [[Tile() for y in range(self.MAP_HEIGHT)] for x in range(self.MAP_WIDTH)]
        # map = [Tile() for x in range(self.MAP_HEIGHT * self.MAP_WIDTH)]
        self.spawn_nodes = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                map[x][y].build_from_bitmask(bitmask_map[x * self.MAP_HEIGHT + y])
                if map[x][y].spawn_node:
                    self.create_spawn_node(x, y, game, map)
        self.map = map
        return self.map

    def return_spawn_nodes(self):
        return self.spawn_nodes

    def load_map(self, map):
        pass

    def setup_new_map(self):
        self.spawn_nodes = []
        self.gEngine.map_init_level(self.MAP_WIDTH, self.MAP_HEIGHT)
        map = [[Tile(True)
                for y in range(self.MAP_HEIGHT)]
               for x in range(self.MAP_WIDTH)]
        self.map = map

        map2x = [[Tile(True)
                  for y in range(self.MAP_HEIGHT * 2)]
                 for x in range(self.MAP_WIDTH * 2)]
        self.map2x = map2x

    def create_spawn_node(self, x, y, game=None, map=None):
        # #spawn nodes will have a turn in the ticker,
        ##undiscovered node will have a higher speed.
        ##Nodes in FoV will do nothing
        if not map:
            map = self.map
        map[x][y].spawn_node = True
        node = SpawnNode(map[x][y], x, y, game)
        node_obj = Object()
        node_obj.node = node
        node_obj.use = node.spawn_mobs
        node_obj.node.owner = node_obj
        node_obj.node.ticker.schedule_turn(0, node_obj)
        self.spawn_nodes.append(node_obj)

    def make_map(self, game=None, depth=0, empty=False, light_handler=None):
        # TODO remove game related logic and move to a populate class/file/method
        self.gEngine.log_message('Creating map.')
        # if game:
        #    game.objects = [game.player]
        # fill map with "blocked" tiles
        rand = libtcod.random_get_instance()  # TODO create random isntance in engine and pass around where needed
        self.setup_new_map()
        # level = Level()
        rooms = []
        num_rooms = 0
        for r in range(self.MAX_ROOMS):
            # random width and height
            w = libtcod.random_get_int(rand, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            h = libtcod.random_get_int(rand, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            # random position without going out of the boundaries of the map
            x = libtcod.random_get_int(rand, 0, self.MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(rand, 0, self.MAP_HEIGHT - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room, game)

                rooms.append(new_room)

                # add some contents to this room, such as monsters
                if not empty:
                    if game:
                        self.place_light(new_room, rand, game, light_handler)
                        self.place_objects(new_room, game, rand)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    if game:
                        # this is the first room, where the player starts at

                        game.player.x = int(new_x)
                        game.player.y = int(new_y)

                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # draw a coin (random number that is either 0 or 1)
                    if libtcod.random_get_int(rand, 0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        if game:
            # Stairs, upstairs get placed under the player
            m = Misc(type='up')
            up = Object(game.dungeon_console, game.player.x, game.player.y, '<', 'set of stairs going up',
                        libtcod.white,
                        blocks=False, misc=m)
            game.objects.append(up)
            up.send_to_back(game.objects)

            # Down stairs get randomly placed.

            if depth < MAX_DEPTH:
                down_placed = False
                while not down_placed:
                    x = libtcod.random_get_int(rand, 0, self.MAP_WIDTH - w - 1)
                    y = libtcod.random_get_int(rand, 0, self.MAP_HEIGHT - h - 1)
                    # only place it if the tile is not blocked
                    if not self.is_blocked(x, y):
                        m = Misc(type='down')
                        down = Object(game.dungeon_console, x, y, '>', 'set of stairs going down', libtcod.white,
                                      blocks=False, misc=m)
                        game.objects.append(down)
                        down.send_to_back(game.objects)
                        down_placed = True

            for object in game.objects:
                object.message = game.message
                object.objects = game.objects

        self.gEngine.map_clear()
        self.set_draw_map(self.map)
        fov_map = self.gEngine.get_fov_map()
        mmap = self.gEngine.get_map()
        self.gEngine.log_message(len(self.map))
        #self.gEngine.lightmask_set_persistent_lightmask()
        if game:
            return Level(self.MAP_WIDTH, self.MAP_HEIGHT, self.gEngine, self.map, game.objects, depth, fov_map, mmap,
                         self.spawn_nodes, rooms)
        else:
            return Level(self.MAP_WIDTH, self.MAP_HEIGHT, self.gEngine, self.map, fov_map=fov_map)

    def set_draw_map(self, map):
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                c = map[x][y]
                self.gEngine.lightmask_set_opacity_value(x, y, c.opacity)
                self.gEngine.map_add_tile(x, y, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node, c.color,
                                          c.opacity)
        self.gEngine.map_init_level(self.MAP_WIDTH, self.MAP_HEIGHT)

    def set_draw_map_2x(self, map):  # converts a normal generated level into a subcell compatable map
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                c = map[x][y]
                self.map2x[x * 2][y * 2] = c
                self.map2x[x * 2 + 1][y * 2] = c
                self.map2x[x * 2][y * 2 + 1] = c
                self.map2x[x * 2 + 1][y * 2 + 1] = c
                self.gEngine.map_add_tile_2x(x * 2, y * 2, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node,
                                             c.color, c.opacity)
                self.gEngine.map_add_tile_2x(x * 2 + 1, y * 2, c.tile, c.blocked, c.block_sight, c.explored,
                                             c.spawn_node,
                                             c.color, c.opacity)
                self.gEngine.map_add_tile_2x(x * 2, y * 2 + 1, c.tile, c.blocked, c.block_sight, c.explored,
                                             c.spawn_node,
                                             c.color, c.opacity)
                self.gEngine.map_add_tile_2x(x * 2 + 1, y * 2 + 1, c.tile, c.blocked, c.block_sight, c.explored,
                                             c.spawn_node, c.color, c.opacity)

    def place_light(self, room, random_instance, game, light_handler):
        x = libtcod.random_get_int(random_instance, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(random_instance, room.y1 + 1, room.y2 - 1)
        i = libtcod.random_get_float(random_instance, 0.75, 1.0)
        if light_handler:
            l = lights.Light(x, y, light_handler, flicker=True, intensity=i)
            light_handler.add_light(l)
        else:
            l = lights.Light(x, y, game.light_handler, flicker=True, intensity=i)
            game.light_handler.add_light(l)

    def place_objects(self, room, game, random_instance):
        if game:
            object_container = game.objects
            # choose random number of items
            num_items = libtcod.random_get_int(random_instance, 0, self.MAX_ROOM_ITEMS)

            for i in range(num_items):
                # choose random spot for this item
                x = libtcod.random_get_int(random_instance, room.x1 + 1, room.x2 - 1)
                y = libtcod.random_get_int(random_instance, room.y1 + 1, room.y2 - 1)

                # only place it if the tile is not blocked
                if not self.is_blocked(x, y, game):
                    dice = libtcod.random_get_int(random_instance, 0, 100)
                    if dice < 70:
                        # create a healing potion (70% chance)
                        object_container.append(game.build_objects.build_potion(game, x, y))

                    else:
                        # create a random scroll (30% chance to get 1 of 3 scrolls (10% chance per scroll))
                        object_container.append(game.build_objects.build_scroll(game, x, y))

    def is_blocked(self, x, y, game=None):
        # first test the map tile
        if self.map[x][y].blocked:
            return True
        if game:
            # now check for any blocking objects
            for object in game.objects:
                if object.blocks and object.x == x and object.y == y:
                    return True

        return False
