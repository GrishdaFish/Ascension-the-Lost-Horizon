__author__ = 'Grishnak'
import tcod as libtcod
from dungeon import dungeon
from dungeon import prefab_dungeon
from gEngine.utilities.dijikstra_map import *
from copy import deepcopy
import math


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
        self.rooms = None


class Light:
    def __init__(self, x, y, r, i, color):
        self.x = x
        self.y = y
        self.radius = r
        self.intensity = i
        if isinstance(color, libtcod.Color):
            r, g, b = color
            r = r * i
            g = g * i
            b = b * i
            r = float(r / 255)
            g = float(g / 255)
            b = float(b / 255)
            color = (r, g, b)
        self.color = color


class NewLightmask:
    def __init__(self, width, height, ambient=0.1):
        self.width = width
        self.height = height
        self.ambient = ambient
        self.lightmask = [(ambient, ambient, ambient) for i in range(width*height)]
        self.lights = []

    def idx(self, x, y):
        return x + y * self.width

    def reset(self):
        self.lightmask = [(self.ambient, self.ambient, self.ambient) for i in range(self.width * self.height)]
        self.lights = []

    def set_ambient(self, ambient):
        self.ambient = ambient

    def calculate_light(self, light, dungeon):
        """
        Calculates the lights with psuedo ray casting
        :param light: The light to calculate
        :param dungeon: the dungeon map isntance to check for walls
        :return: nothing
        """
        # first create a bounding box for the light, clamped to map boundaries
        top = int(max(0, light.y - light.radius + 1))
        bottom = int(min(self.height, light.y + light.radius + 1))
        left = int(max(0, light.x - light.radius + 1))
        right = int(min(self.width, light.x + light.radius + 1))
        # then we cast the top and bottom rays from left to right, from the light's center point
        for x in range(left, right):
            top_ray = libtcod.line_iter(light.x, light.y, x, top)
            for cell in top_ray:
                # and clamp to the circle, so we don't try to walk the ray past the radius of the circle
                if self.in_circle(light.x, light.y, cell[0], cell[1], light.radius):
                    # then we check to see if we hit a wall, if we do, light it, and stop walking through the line
                    # since we don't want to light past a wall
                    if dungeon[cell[0]][cell[1]].blocked:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                        break
                    else:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                else:
                    break
            # follow the same process for the bottom line
            bottom_ray = libtcod.line_iter(light.x, light.y, x, bottom)
            for cell in bottom_ray:
                if self.in_circle(light.x, light.y, cell[0], cell[1], light.radius):
                    if dungeon[cell[0]][cell[1]].blocked:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                        break
                    else:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                else:
                    break
        # And then cast the left and right rays, from top to bottom
        for y in range(top, bottom):
            left_ray = libtcod.line_iter(light.x, light.y, left, y)
            for cell in left_ray:
                if self.in_circle(light.x, light.y, cell[0], cell[1], light.radius):
                    if dungeon[cell[0]][cell[1]].blocked:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                        break
                    else:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                else:
                    break
            right_ray = libtcod.line_iter(light.x, light.y, right, y)
            for cell in right_ray:
                if self.in_circle(light.x, light.y, cell[0], cell[1], light.radius):
                    if dungeon[cell[0]][cell[1]].blocked:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                        break
                    else:
                        d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
                        self.light_tile(cell[0], cell[1], d, light)
                else:
                    break
        # # then loop through the box
        # for y in range(top, bottom):
        #     for x in range(left, right):
        #         # then make sure the tile we are checking is within the circle radius
        #         # Note, circles look better at n.5 radius
        #         if self.in_circle(light.x, light.y, x, y, light.radius):
        #             # next, create a line from the center point of the light, to the destination tile
        #             shadow = libtcod.line_iter(light.x, light.y, x, y)
        #             blocked = False
        #             # walk through the path to to see if there is a wall
        #             for cell in shadow:
        #                 if dungeon[cell[0]][cell[1]].blocked:
        #                     # if we find one, we light it up, then prevent any further tiles from being lit
        #                     d = self.distance_from_center(light.x, light.y, cell[0], cell[1], light.radius)
        #                     self.light_tile(cell[0], cell[1], d, light)
        #                     blocked = True
        #                     break
        #             # if no wall was found, the tile can be lit
        #             if not blocked:
        #                 d = self.distance_from_center(light.x, light.y, x, y, light.radius)
        #                 self.light_tile(x, y, d, light)

    def light_tile(self, x, y, amount, light):
        """
        calculates the light value based on distance from center
        :param x: x position of the tile to be lit
        :param y: y position of t he tile to be lit
        :param amount: the distance from the center
        :param light: the Light() class
        :return: nothing
        """
        # divide by radius to get a distance normalized float to  use
        d = amount / light.radius
        c1 = -d + light.color[0]
        c2 = -d + light.color[1]
        c3 = -d + light.color[2]

        cc1, cc2, cc3 = self.lightmask[self.idx(x, y)]

        c1 = max(c1, cc1)
        c2 = max(c2, cc2)
        c3 = max(c3, cc3)

        c1 = max(self.ambient, c1)
        c2 = max(self.ambient, c2)
        c3 = max(self.ambient, c3)
        self.lightmask[self.idx(x, y)] = (c1, c2, c3)

    def add_light(self, x, y, intensity, color, radius=20.5):
        light = Light(x, y, radius, intensity, color)
        self.lights.append(light)

    def compute(self, dungeon=None):
        for light in self.lights:
            self.calculate_light(light, dungeon)

    def get_value(self, x, y):
        return (self.lightmask[self.idx(x, y)])

    @staticmethod
    def in_circle(centerx, centery, targetx, targety, radius):
        dx = targetx - centerx
        dy = targety - centery
        sq = (dx*dx + dy*dy)
        return sq < radius*radius

    @staticmethod
    def distance_from_center(cx, cy, tx, ty, r):
        dx = cx - tx
        dy = cy - ty
        sq = dx * dx + dy * dy
        d = math.sqrt(sq)
        return d


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
        self.light_mask = NewLightmask(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
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
        # self.level.dungeon, self.level.rooms = self.dungeon_gen.add_prefab_room(self.level.dungeon,
        #                                                       self.dungeon_gen.width,
        #                                                       self.dungeon_gen.height,
        #                                                       True,
        #                                                       self.level.rooms,
        #                                                       True)
        self.level = self.dungeon_gen.level_from_prefabs()
        # self.height_map = libtcod.heightmap_new(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        # noise = libtcod.noise_new(libtcod.random_get_int(0, 3, 5))
        # libtcod.heightmap_add_fbm(self.height_map, noise, 2.5, 0.5, 1.0, 1.0, 5, 0.5, 0.5)
        # for y in range(self.level.MAP_HEIGHT):
        #     for x in range(self.level.MAP_WIDTH):
        #         self.level.dungeon[x][y].color = libtcod.Color(255,255,255)
        #         v = libtcod.heightmap_get_value(self.height_map, x, y)
        #         self.level.dungeon[x][y].color *= v

        self.gEngine.map_init_level(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        self.dungeon_gen.set_draw_map(self.level.dungeon)

        self.gEngine.map_init_level(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        self.level.fov_map = self.gEngine.get_fov_map()
        self.canopy = self.gEngine.console_new(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        self.canopy_backup = self.gEngine.console_new(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
        libtcod.console_set_key_color(self.gEngine.console_get_console(self.canopy), (0, 0, 0))
        for y in range(self.level.MAP_HEIGHT):
            for x in range(self.level.MAP_WIDTH):
                self.gEngine.console_get_console(self.canopy).buffer[y, x] = (ord(' '), [0,0,0,0], [0,0,0,0])
        self.lights = []

    def run(self, key, mouse):
        while not libtcod.console_is_window_closed():
            self.gEngine.console_clear(self.con)
            #self.gEngine.console_clear(self.canopy)
            key = libtcod.Key()
            mouse = libtcod.Mouse()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
            libtcod.map_compute_fov(self.level.fov_map, mouse.cx, mouse.cy)
            self.gEngine.lightmask_reset()
            self.light_mask.reset()
            for lights in self.lights:
                self.light_mask.add_light(lights[0], lights[1], lights[2], lights[3], lights[4])
            self.testing(key, mouse)

            self.light_mask.compute(self.level.dungeon)
            #self.gEngine.lightmask_compute(self.level.dungeon)
            self.gEngine.map_draw(self.con, mouse.cx, mouse.cy, run_fov=False, lightmask=self.light_mask)
            #self.gEngine.map_draw_fast(self.con, mouse.cx, mouse.cy)
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
            self.gEngine.console_blit(self.canopy, 0, 0, 0, 0, 0, 0, 0, 0.0, 1.0)
            self.gEngine.console_flush()

        return True

    def testing(self, key, mouse):
        cx, cy = 0, 0
        self.gEngine.console_print(self.con, 1, 1, "(%dfps) Depth: %d" % (libtcod.sys_get_fps(), 1))
        if mouse.cx < self.level.MAP_WIDTH and mouse.cy < self.level.MAP_HEIGHT:
            flicker = 0.0  # libtcod.random_get_float(0, -0.25, 0.25)
            intensity_flicker = libtcod.random_get_float(0, -0.05, 0.05)

            self.light_mask.add_light(mouse.cx, mouse.cy, 1.35+intensity_flicker, libtcod.white, 20.5 + flicker)
            # radius = 2.5
            # top = int(max(1, mouse.cy - radius + 1))
            # bottom = int(min(self.level.MAP_HEIGHT-1, mouse.cy + radius + 1))
            # left = int(max(1, mouse.cx - radius + 1))
            # right = int(min(self.level.MAP_WIDTH-1, mouse.cx + radius + 1))
            # for y in range(top-1, bottom+1):
            #     for x in range(left-1, right+1):
            #         #if self.in_circle(mouse.cx, mouse.cy, x, y, radius):
            #             self.gEngine.console_get_console(self.canopy).buffer[y, x][2][3] = 255
            #
            # for y in range(top, bottom):
            #     for x in range(left, right):
            #         if self.in_circle(mouse.cx, mouse.cy, x, y, radius):
            #             dx = mouse.cx - x
            #             dy = mouse.cy - y
            #             sq = dx * dx + dy * dy
            #             d = math.sqrt(sq)
            #             d = d / radius
            #             d = d / 1.755
            #             v = 255 * d
            #             self.gEngine.console_get_console(self.canopy).buffer[y, x][2][3] = v

        if key.vk == libtcod.KEY_SPACE:
            x = libtcod.random_get_int(0, 1, self.level.MAP_WIDTH)
            y = libtcod.random_get_int(0, 1, self.level.MAP_HEIGHT)
            self.lights.append((x, y, 1.5, libtcod.desaturated_orange, 20.5))
            # tree_colors = [(libtcod.desaturated_green, libtcod.darkest_green),
            #                (libtcod.desaturated_red, libtcod.darkest_red),
            #                (libtcod.desaturated_orange, libtcod.darkest_orange),
            #                (libtcod.desaturated_yellow, libtcod.darkest_yellow)
            #                ]
            # tree_color = tree_colors[libtcod.random_get_int(0, 0, len(tree_colors)-1)]
            # radius = libtcod.random_get_int(0, 3,  5)
            # radius += 0.5
            # nodes = libtcod.random_get_int(0, 6, 11)
            # centerx = mouse.cx
            # centery = mouse.cy
            # multiplier = 1
            # for n in range(nodes):
            #     #tree_color = tree_colors[libtcod.random_get_int(0, 0, len(tree_colors) - 1)]
            #     multiplier = n / nodes
            #     nodex = libtcod.random_get_float(0, -radius, radius)
            #     nodey = libtcod.random_get_float(0, -radius, radius)
            #     nodex = centerx + nodex
            #     nodey = centery + nodey
            #     self.draw_tree(nodex, nodey, radius, multiplier, tree_color)
            # self.draw_tree(centerx, centery, radius, colors=tree_color)
            #
            # self.dungeon_gen.set_draw_map(self.level.dungeon)
            #
            # self.gEngine.map_init_level(self.level.MAP_WIDTH, self.level.MAP_HEIGHT)
            # self.level.fov_map = self.gEngine.get_fov_map()

        if mouse.lbutton_pressed:
            pass
            # print(self.gEngine.console_get_console(self.con).buffer[0,0])
            # self.gEngine.console_get_console(self.con).buffer[0,0] = (32, [0,0,0,0], [255,255,255,0])
            # print(self.gEngine.console_get_console(self.con).buffer[0, 0])

        if mouse.rbutton:
            pass
        if mouse.mbutton_pressed:
            pass

        if key.vk == libtcod.KEY_ENTER:
            pass

    def in_circle(self, cx, cy, tilex, tiley, r):
        dx = float(tilex - cx)
        dy = float(tiley - cy)
        sq = float(dx*dx + dy*dy)
        return sq < r*r

    def draw_tree(self, center_x, center_y, radius, layer_multiplier=1.0, colors=None):
        layer_multiplier = max(0.1, layer_multiplier)
        top = int(max(0, center_y - radius + 1))
        bottom = int(min(self.level.MAP_HEIGHT, center_y + radius + 1))
        left = int(max(0, center_x - radius + 1))
        right = int(min(self.level.MAP_WIDTH, center_x + radius + 1))
        for y in range(top, bottom):
            for x in range(left, right):
                if self.in_circle(center_x, center_y, x, y, radius):
                    dx = center_x - x
                    dy = center_y - y
                    sq = dx * dx + dy * dy
                    d = math.sqrt(sq)
                    d = d / radius
                    variance = libtcod.random_get_float(0, 1.0, 1.75)
                    d = (d / variance)
                    d = d * (layer_multiplier)
                    col = libtcod.color_lerp(colors[1], colors[0],  d)
                    #self.level.dungeon[x][y].color = col
                    self.gEngine.console_get_console(self.canopy).buffer[y, x] = (ord(' '), [0, 0, 0, 0],[col[0], col[1], col[2], 255])
                    self.gEngine.console_get_console(self.canopy_backup).buffer[y, x] = (ord(' '), [0, 0, 0, 0], [col[0], col[1], col[2], 255])
