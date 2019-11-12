
class Level:
    def __init__(self, width, height, gEngine, dungeon=None, objects=None, depth=None, fov_map=None, draw_map=None,
                 spawn_nodes=None, rooms=None):
        self.dungeon = dungeon
        self.objects = objects
        self.depth = depth
        self.fov_map = fov_map
        self.draw_map = draw_map
        self.spawn_nodes = spawn_nodes
        self.MAP_HEIGHT = height
        self.MAP_WIDTH = width
        self.gEngine = gEngine
        self.map2x = [[' ' for y in range(height*2)] for x in range(width*2)]

        if rooms:
            self.rooms = rooms
        else:
            self.rooms = []

    def update_level(self, dungeon, objects, fov_map, draw_map):
        self.dungeon = dungeon
        self.objects = objects
        self.fov_map = fov_map
        self.draw_map = draw_map

    def add_room(self, room):
        self.rooms.append(room)

    def set_draw_map(self):
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                c = self.draw_map[x][y]
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
                self.gEngine.map_add_tile_2x(x * 2 + 1, y * 2, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node,
                                        c.color, c.opacity)
                self.gEngine.map_add_tile_2x(x * 2, y * 2 + 1, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node,
                                        c.color, c.opacity)
                self.gEngine.map_add_tile_2x(x * 2 + 1, y * 2 + 1, c.tile, c.blocked, c.block_sight, c.explored,
                                        c.spawn_node, c.color, c.opacity)