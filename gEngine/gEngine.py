# #Python prototype for the c++ pyd
##Basicly a wrapper around libtcod, like the pyd is
##Used incase the pyd is absent so the code wont break.
##pretty much a c++ port, not very pythonic, doesnt need to be.
##Might clean it up later
# TODO: remove r, g, b from method calls and accept  tcod color, then grab r, g, b in the engine to simply calls


import imp
import tcod as libtcod
import logging
import sys
import os
import numpy as np

RELEASE = False
if RELEASE:
    path = getattr(sys, "_MEIPASS", ".")
else:
    path = sys.path[0]
try:
    path = os.path.join(path, 'gEngine', 'pyds', 'gEngine', 'pyds')
    fp, pathname, description = imp.find_module('cy_light_mask', [path])
    light_mask = imp.load_module('cy_light_mask', fp, pathname, description)
except ImportError as e:
    print(e)
    from gEngine import light_mask

from gEngine import particle
from gEngine import draw
from gEngine.utilities import logging
from gEngine.utilities import status_bar
from gEngine.utilities import options as _options
from gEngine.utilities import config


def in_rect(x, y, w, h):
    return x < w and y < h


class Tile:
    def __init__(self, x=0, y=0, cell='#', blocked=True, block_sight=True,
                 explored=False, spawn_node=None, color=(0, 0, 0), opacity=1.0):
        self.x = x
        self.y = y
        self.cell = cell
        self.blocked = blocked
        self.block_sight = block_sight
        self.explored = explored
        self.spawn_node = spawn_node
        self.color = color
        self.opacity = opacity


class gEngine:
    def __init__(self):
        self.engine_options = config.EngineConfig()
        self.options = _options.GameOptions()
        self.options.load_options()

        self.w = self.engine_options.screen_width
        self.h = self.engine_options.screen_height
        self.SCREEN_WIDTH = self.w
        self.SCREEN_HEIGHT = self.h

        self.name = self.engine_options.name + ' ' + self.engine_options.version
        self.fs = self.options.fullscreen
        self.fps = self.options.fps

        self.console_set_custom_font(self.engine_options.font,
                                     self.engine_options.font_layout |
                                     self.engine_options.font_type)

        self.mConsole = []
        self.mMap = []
        self.mMap2x = []
        self.mImages = []
        self.FOV = None

        self.color_dark_wall = libtcod.darkest_grey
        self.color_light_wall = libtcod.Color(99, 99, 99)
        self.color_dark_ground = libtcod.darker_grey
        self.color_light_ground = libtcod.Color(125, 125, 125)
        self.color_tile_wall = libtcod.Color(177, 177, 177)
        self.color_tile_ground = libtcod.Color(190, 190, 190)

        self.light_sources = []
        self.noise = libtcod.noise_new(1, libtcod.NOISE_SIMPLEX)

        self.lightmask = light_mask.LightMask(self.w, 48)

        self.particles = []
        self.modules = []

        self.key = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.root = None
        self.logger = logging.log_manager()

        self.console_id_counter = 0
        self.image_id_counter = 0
        self.image_dict = {}
        self.console_dict = {}
        self.map_image = self.image_new(self.w, self.h)
        self.subcell_map_image = self.image_new(self.w * 2, self.h * 2)
        self.light_map = self.image_new(self.w, self.h)
        self.subcell_light_map = self.image_new(self.w * 2, self.h * 2)

    def run(self):
        is_closed = None
        while not is_closed:
            is_closed = libtcod.console_is_window_closed()
            # self.console_clear_all()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, k=self.key, m=self.mouse)
            for module in self.modules:
                if module.active is True:
                    is_closed = module.run(self.key, self.mouse)
            # self.render_all()

    def render_all(self):
        self.console_flush()

    def add_module(self, module):
        self.modules.append(module)

    def remove_module(self, module):
        module.on_exit()

    def log_message(self, message, level='info'):
        if level == 'info':
            self.logger.log.info(message)
        elif level == 'debug':
            self.logger.log.debug(message)
        elif level == 'error':
            self.logger.log.error(message)
        else:
            self.logger.log.info(message)

    def logger_set_level(self, level='debug'):
        pass

    def init_root(self):  # Root's id will ALWAYS be 0.
        self.root = libtcod.console_init_root(self.w, self.h, self.name, self.fs, renderer=libtcod.RENDERER_OPENGL2)
        libtcod.sys_set_fps(self.fps)
        self.console_dict[self.console_id_counter] = self.root
        self.console_id_counter += 1

    def console_set_key_color(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        libtcod.console_set_key_color(self.console_dict[con], col)

    # @staticmethod
    def console_set_custom_font(self, font_file, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, h=0, v=0):
        font_file = font_file.replace('core.exe', '')
        libtcod.console_set_custom_font(font_file, flags, h, v)

    def console_new(self, width, height):
        self.console_dict[self.console_id_counter] = libtcod.console.Console(int(width), int(height))
        c = self.console_id_counter
        self.console_id_counter += 1
        return c

    def console_flush(self):
        libtcod.console_flush()

    def console_clear_all(self):
        for con in self.console_dict:
            con.clear()

    def console_clear(self, con):
        self.console_dict[con].clear()

    def console_remove_console(self, con):
        if con > 1:  # so we dont try to delete root
            c = self.console_dict.pop(con)
            libtcod.console_delete(c)

    def console_remove_all(self):
        self.mConsole = []
        self.console_dict = {}
        self.console_id_counter = 0
        self.console_dict[self.console_id_counter] = self.root
        self.console_id_counter += 1

    def console_get_height_rect(self, con, x, y, width, height, fmt):
        return libtcod.console_get_height_rect(self.console_dict[con], x, y, width, height, fmt)

    def console_set_default_foreground(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        libtcod.console_set_default_foreground(self.console_dict[con], col)

    def console_set_default_background(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        libtcod.console_set_default_background(self.console_dict[con], col)

    def console_print_frame(self, con, x, y, width, height, clear):
        libtcod.console_print_frame(self.console_dict[con], int(x), int(y), int(width), int(height), clear)

    def console_print_rect(self, con, x, y, width, height, fmt):
        libtcod.console_print_rect(self.console_dict[con], int(x), int(y), int(width), int(height), fmt)

    def console_blit(self, conSrc, xSrc, ySrc, wSrc, hSrc, conDest, xDest, yDest, foreAlph=1.0, backAlph=1.0):
        src = self.console_dict[conSrc]
        if conDest == 0:
            dest = self.root
        else:
            dest = self.console_dict[conDest]
        src.blit(dest, int(xDest), int(yDest), int(xSrc), int(ySrc), int(wSrc), int(hSrc), foreAlph, backAlph)

    def console_put_char_ex(self, con, x, y, c, cr, cg, cb, br, bg, bb):
        fore = libtcod.Color(cr, cg, cb)
        back = libtcod.Color(br, bg, bb)
        libtcod.console_put_char_ex(self.console_dict[con], x, y, c, fore, back)

    def console_set_char(self, con, x, y, c):
        libtcod.console_set_char(self.console_dict[con], x, y, c)

    def console_set_alignment(self, con, align):  # Depreciated. Requires refactor then removal
        libtcod.console_set_alignment(self.console_dict[con], align)

    def console_print(self, con, x, y, fmt):
        libtcod.console_print(self.console_dict[con], int(x), int(y), fmt)

    def console_print_ex(self, con, x, y, flag, alignment, fmt):
        libtcod.console_print_ex(self.console_dict[con], x, y, flag, alignment, fmt)

    def console_get_char_background(self, con, x, y):
        col = libtcod.console_get_char_background(self.console_dict[con], x, y)
        return libtcod.color_get_hsv(col)

    def console_get_char_foreground(self, con, x, y):
        col = libtcod.console_get_char_foreground(self.console_dict[con], x, y)
        return col

    def image_new(self, x, y):
        self.image_dict[self.image_id_counter] = libtcod.image.Image(x, y)
        c = self.image_id_counter
        self.image_id_counter += 1
        return c

    def image_load(self, path):
        img = libtcod.image_load(path)
        x, y = libtcod.image_get_size(img)
        img2 = libtcod.image.Image(x, y)
        for xx in range(x):
            for yy in range(y):
                img2.put_pixel(xx, yy, img.get_pixel(xx, yy))
        self.image_dict[self.image_id_counter] = img2
        c = self.image_id_counter
        self.image_id_counter += 1
        return c

    def image_delete(self, img):
        self.image_dict.pop(img)

    def image_clear(self, i, r, g, b):
        col = libtcod.Color(r, g, b)
        self.image_dict[i].clear(col)

    def image_put_pixel(self, i, x, y, r, g, b):
        col = libtcod.Color(r, g, b)
        self.image_dict[i].put_pixel(x, y, col)

    def image_get_size(self, i):
        w = self.image_dict[i].width
        h = self.image_dict[i].height
        return w, h

    def image_get_pixel(self, i, x, y):
        return self.image_dict[i].get_pixel(x, y)

    def image_blit(self, i, c, x, y, w=-1, h=-1):
        self.image_dict[i].blit(self.console_dict[c], float(x), float(y), libtcod.BKGND_SET, 1.0, 1.0, 0)

    def image_blit_2x(self, i, c, x, y, sx=0, sy=0, w=-1, h=-1):
        self.image_dict[i].blit_2x(self.console_dict[c], x, y, sx, sy, w, h)

    def image_replace(self, image, replacement):
        self.image_dict[image] = replacement

    def map_init_level(self, sizeX, sizeY):
        self.FOV = libtcod.map_new(sizeX, sizeY)
        for tile in self.mMap:
            # tile.explored = False
            self.map_set_properties(tile.x, tile.y, not tile.blocked, not tile.block_sight)

    def map_add_tile(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_add_tile_2x(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap2x.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_set_properties(self, x, y, blocked, block_sight):
        libtcod.map_set_properties(self.FOV, x, y, blocked, block_sight)

    def map_clear(self):
        self.mMap = []
        self.mMap2x = []

    def set_fov_map(self, map):
        self.FOV = map

    def get_fov_map(self):
        return self.FOV

    def get_map(self):
        return self.mMap

    def get_map_tile(self, x, y):
        return self.mMap[x + y * self.w]

    def set_map(self, mMap):
        self.mMap = mMap

    def set_map_2x(self, map2x):
        self.mMap2x = map2x

    def get_map_2x(self):
        return self.mMap2x

    def map_draw_2x(self, con, x, y):
        self.image_clear(self.subcell_map_image, 0, 0, 0)
        if con == 0:
            for tile in self.mMap2x:
                r, g, b = tile.color
                brightness = self.lightmask.mask[tile.x + tile.y * (self.w * 2)]
                r *= brightness[0]
                g *= brightness[1]
                b *= brightness[2]
                self.image_put_pixel(self.subcell_map_image, tile.x, tile.y, int(r), int(g), int(b))
                '''if tile.block_sight:
                    r, g, b = self.color_light_wall
                    self.image_put_pixel(self.subcell_map_image, tile.x, tile.y, r, g, b)
                else:
                    r,g,b = self.color_light_ground
                    self.image_put_pixel(self.subcell_map_image, tile.x, tile.y, r, g, b)'''

            self.console_clear(con)
            self.image_blit_2x(self.subcell_map_image, con, 0, 0)

    def clamp_float(self, f, l=1):
        return f - f % 1e-2

    def map_get_final_color(self, x, y):
        r, g, b = self.mMap[x][y].color
        if libtcod.map_is_in_fov(self.FOV, x, y):
            brightness = self.lightmask_get_mask_value(x, y)
            new_bright = []
            for f in range(len(brightness)):
                new_bright.append(self.clamp_float(brightness[f]))
            brightness = new_bright
            # print(brightness)
            # this is  VERY slow for some reason
            r *= brightness[0]
            g *= brightness[1]
            b *= brightness[2]
            self.mMap[x][y].explored = True
        else:
            if self.mMap[x][y].explored:
                r *= self.lightmask.ambient
                g *= self.lightmask.ambient
                b *= self.lightmask.ambient

            else:
                r, g, b = 0, 0, 0
        return int(r), int(g), int(b)

    def map_draw_fast(self, con, xx, yy):
        # self.image_clear(self.map_image, 0, 0, 0)

        if con == 0:
            con = self.root
        new_img_array = np.array([[self.map_get_final_color(x, y) for y in range(48)] for x in range(self.w)])
        ##arr = np.asarray(new_img_array)
        arr = new_img_array.transpose(1, 0, 2)
        self.image_replace(self.map_image, libtcod.image.Image.from_array(arr))
        self.image_blit(self.map_image, con, self.w / 2, self.h / 2 - 4)

    def map_draw(self, con, x=0, y=0, run_fov=True):
        self.image_clear(self.map_image, 0, 0, 0)
        if con == 0:
            con = self.root
        for tile in self.mMap:
            r, g, b = tile.color
            if run_fov:
                if libtcod.map_is_in_fov(self.FOV, tile.x, tile.y):
                    brightness = self.lightmask_get_mask_value(tile.x, tile.y)
                    new_bright = []
                    for f in range(len(brightness)):
                        new_bright.append(self.clamp_float(brightness[f]))
                    brightness = new_bright
                    # print(brightness)
                    # this is  VERY slow for some reason
                    r *= brightness[0]
                    g *= brightness[1]
                    b *= brightness[2]
                    tile.explored = True
                else:
                    if tile.explored:
                        r *= self.lightmask.ambient
                        g *= self.lightmask.ambient
                        b *= self.lightmask.ambient

                    else:
                        r, g, b = 0, 0, 0
            self.image_put_pixel(self.map_image, tile.x, tile.y, int(r), int(g), int(b))
        self.image_blit(self.map_image, con, self.w / 2, self.h / 2)

    def map_draw_scrolling(self, con, game, x, y):
        self.image_clear(self.map_image, 0, 0, 0)
        if con == 0:
            pass
        else:
            # libtcod.map_compute_fov(self.FOV, x, y, 5, True, libtcod.FOV_SHADOW)
            cx = game.player.x - (game.Map.MAP_WIDTH / 2)
            cy = game.player.y - (game.Map.MAP_HEIGHT / 2)
            minx, miny = game.Map.MAP_WIDTH, game.Map.MAP_HEIGHT
            for x in range(minx):
                dx = x + cx
                for y in range(miny):
                    dy = y + cy
                    if in_rect(dx, dy, minx, miny):
                        tile = game.Map.map[dx][dy]
                        if libtcod.map_is_in_fov(self.FOV, dx, dy):
                            if tile.block_sight:
                                r, g, b = self.color_light_wall
                                self.image_put_pixel(self.map_image, x, y, r, g, b)
                            else:
                                r, g, b = self.color_light_ground
                                self.image_put_pixel(self.map_image, x, y, r, g, b)
                            tile.explored = True
                        else:
                            if tile.explored:
                                if tile.block_sight:
                                    r, g, b = self.color_dark_wall
                                    self.image_put_pixel(self.map_image, x, y, r, g, b)
                                else:
                                    r, g, b = self.color_dark_ground
                                    self.image_put_pixel(self.map_image, x, y, r, g, b)
            self.console_clear(con)
            self.image_blit(self.map_image, con, self.w / 2, self.h / 2)

    def map_is_explored(self, x, y):
        for tile in self.mMap:
            if tile.x == x and tile.y == y:
                return tile.explored

    def lightmask_set_ambient(self, ambient):
        self.lightmask.set_ambient(ambient)

    def lightmask_set_size(self, w, h):
        self.lightmask.width = w
        self.lightmask.height = h
        self.lightmask_reset()

    def lightmask_set_opacity_value(self, x, y, o):
        self.lightmask.set_opacity_value(x, y, o)

    def lightmask_set_persistent_lightmask(self):
        self.lightmask.set_persistent_lightmask()

    def lightmask_reset(self):
        self.lightmask.reset()

    def lightmask_add_light(self, x, y, br):
        self.lightmask.add_light(x, y, br)

    def lightmask_set_intensity(self, i):
        self.lightmask.set_intensity(i)

    def lightmask_compute(self, map):
        self.lightmask.compute_mask(map)

    def lightmask_get_mask_value(self, x, y):
        return self.lightmask.get_mask_value(x, y)

    def particle_explosion(self, num, x, y, r=False, b=False, color=None):
        particle.explosion(num, self.particles, x, y, r, b, color)

    def particle_nova(self, num, x, y, r=False, b=False):
        particle.nova(num, self.particles, x, y, r, b)

    def particle_cone_spray(self, num, ox, oy, dx, dy, r=False, b=False):
        particle.cone_spray(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_cone(self, num, ox, oy, dx, dy, r=False, b=False):
        particle.cone(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_projectile(self, num, ox, oy, dx, dy, r=False, b=False, color=None):
        particle.projectile(num, self.particles, ox, oy, dx, dy, r, b, color)

    def particle_update(self, map=None):
        for p in range(len(self.particles) - 1, 0, -1):
            self.particles[p].update(self.lightmask, map)
            if self.particles[p].dead:
                self.particles.pop(p)

    def particle_draw(self, con, c='*'):
        for p in self.particles:
            self.console_put_char_ex(con, int(p.x), int(p.y), c, 255, 255, 255, 0, 0, 0)

    # def msgbox(text, width=50, con=None, SCREEN_HEIGHT=50, SCREEN_WIDTH=80):
    #    menu(con, text, [], width, SCREEN_HEIGHT, SCREEN_WIDTH)  # use menu() as a sort of "message box"
