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

RELEASE = True
SUBCELL = True
if RELEASE:
    path = getattr(sys, "_MEIPASS", ".")
else:
    path = sys.path[0]
# try:
#     path = os.path.join(path, 'gEngine', 'pyds', 'gEngine', 'pyds')
#     fp, pathname, description = imp.find_module('cy_light_mask', [path])
#     light_mask = imp.load_module('cy_light_mask', fp, pathname, description)
# except ImportError as e:
#     print(e)
#     from gEngine import light_mask, cEngine
try:
    from gEngine import cEngine
except ImportError as e:
    print(e)
    cEngine = None

from gEngine import particle
from gEngine.utilities import logging
from gEngine.utilities import options as _options
from gEngine.utilities import config
from gEngine import tcod_event
from gEngine.animation import animations


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

        # self.lightmask = light_mask.LightMask(self.w, 48)

        self.particles = []
        self.modules = []

        self.key = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.root = None
        self.logger = logging.log_manager()
        self.engine = None
        self.console_id_counter = 0
        self.image_id_counter = 0
        self.image_dict = {}
        self.console_dict = {}

        self.random_instance = None
        self.random_set_instance()
        self.animation_engine = animations.Animations(self)

    def run(self):
        is_closed = None
        while True:
            self.handle_input()
            for module in self.modules:
                if module.active is True:
                    module.run(None, None)

    def render_all(self):
        self.console_flush()

    def add_module(self, module):
        self.modules.append(module)

    def remove_module(self, module):
        module.on_exit()

    def log_open_block(self, message):
        if cEngine:
            self.engine.mOpenBlock(message)

    def log_close_block(self):
        if cEngine:
            self.engine.mCloseBlock()

    def log_message(self, message, level='info'):
        if cEngine:
            levels = {"info": self.engine.mInfo,
                      "notice": self.engine.mNotice,
                      "error": self.engine.mError,
                      "fatal": self.engine.mFatalError}
            if level in levels:
                levels[level](message)
        # if level == 'info':
        #     self.logger.log.info(message)
        # elif level == 'debug':
        #     self.logger.log.debug(message)
        # elif level == 'error':
        #     self.logger.log.error(message)
        # else:
        #     self.logger.log.info(message)
        pass

    def logger_set_level(self, level='debug'):
        pass

    def handle_input(self, key=None, mouse=None, clear=False):
        key_conv = {
            44: libtcod.KEY_SPACE,
            41: libtcod.KEY_ESCAPE,
            42: libtcod.KEY_BACKSPACE,
            40: libtcod.KEY_ENTER,
            80: libtcod.KEY_LEFT,
            79: libtcod.KEY_RIGHT,
            82: libtcod.KEY_UP,
            81: libtcod.KEY_DOWN,
        }
        if cEngine:
            if not key:
                key = libtcod.Key()
            if not mouse or clear:
                mouse = libtcod.Mouse()
            # TODO THIS CODE IS PERFECTLY FINE. NOTHING TO SEE HERE.
            for event in tcod_event.get():
                if event.type == 'MOUSEMOTION':
                    # TODO: no touchy
                    try:  # to protect my beautiful code
                        self.mouse.cx = int(event.pixel[0] / 16)
                        self.mouse.cy = int(event.pixel[1] / 16)
                    except ZeroDivisionError:
                        pass  # nothing to see here....

                if event.type == 'MOUSEBUTTONDOWN':
                    try:  # Todo move along
                        self.mouse.cx = int(event.pixel[0] / 16)
                        self.mouse.cy = int(event.pixel[1] / 16)
                    except ZeroDivisionError:
                        pass

                    if event.button == tcod_event.BUTTON_LEFT:
                        self.mouse.lbutton = True
                    if event.button == tcod_event.BUTTON_RIGHT:
                        self.mouse.rbutton = True

                if event.type == "MOUSEBUTTONUP":
                    try:  # TODO  JUST KEEP MOVING
                        self.mouse.cx = int(event.pixel[0] / 16)
                        self.mouse.cy = int(event.pixel[1] / 16)
                    except ZeroDivisionError:
                        pass

                    if event.button == tcod_event.BUTTON_LEFT:
                        self.mouse.lbutton = False
                    if event.button == tcod_event.BUTTON_RIGHT:
                        self.mouse.rbutton = False

                if event.type == "TEXTINPUT":
                    key.c = ord(event.text)

                if event.type == "KEYDOWN":
                    if event.scancode in key_conv:
                        key.vk = key_conv[event.scancode]
                if event.type == "WINDOWCLOSE":
                    self.log_close_block()
                    exit(69420)  # lmao
            return key, self.mouse
        else:
            key = libtcod.Key()
            mouse = libtcod.Mouse()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY, key, mouse)
            return key, mouse

    def init_root(self):  # Root's id will ALWAYS be 0.
        if cEngine:
            self.engine = cEngine.gEngine(self.w, self.h, self.name, self.fs, self.fps, self.engine_options.font)
        else:
            self.root = libtcod.console_init_root(self.w, self.h, self.name, self.fs, renderer=libtcod.RENDERER_OPENGL2)
            libtcod.sys_set_fps(self.fps)
            self.console_dict[self.console_id_counter] = self.root
            self.console_id_counter += 1
        self.animation_engine.load_animations()
        self.map_image = self.image_new(self.w, self.h)
        self.subcell_map_image = self.image_new(self.w * 2, self.h * 2)
        self.light_map = self.image_new(self.w, self.h)
        self.subcell_light_map = self.image_new(self.w * 2, self.h * 2)

    def console_set_key_color(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        libtcod.console_set_key_color(self.console_dict[con], col)

    def sys_get_fps(self):
        if cEngine:
            return self.engine.mSysGetFPS()
        else:
            return libtcod.sys_get_fps()

    # @staticmethod
    def console_set_custom_font(self, font_file, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, h=0, v=0):
        if cEngine:
            libtcod.console_set_custom_font(font_file, flags, h, v)
            pass
        else:
            font_file = font_file.replace('core.exe', '')
            libtcod.console_set_custom_font(font_file, flags, h, v)

    def console_new(self, width, height):
        if cEngine:
            return self.engine.mAddConsole(int(width), int(height))
        else:
            self.console_dict[self.console_id_counter] = libtcod.console.Console(int(width), int(height))
            c = self.console_id_counter
            self.console_id_counter += 1
        return c

    def console_flush(self):
        if cEngine:
            self.engine.mFlush()
        else:
            libtcod.console_flush()

    def console_clear_all(self):
        if cEngine:
            pass
        else:
            for con in self.console_dict:
                self.console_dict[con].clear()

    def console_get_console(self, con):
        return self.console_dict[con]

    def console_clear(self, con):
        if cEngine:
            self.engine.mClear(con)
        else:
            self.console_dict[con].clear()

    def console_remove_console(self, con):
        if cEngine:
            if con > 0:
                self.engine.mDestroyConsole(con)
        else:
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
        if cEngine:
            return self.engine.mGetHeightRect(con, x, y, width, height, fmt)
        else:
            return libtcod.console_get_height_rect(self.console_dict[con], x, y, width, height, fmt)

    def console_set_default_foreground(self, con, r, g, b):
        if cEngine:
            self.engine.mSetForegroundColor(con, r, g, b)
        else:
            col = libtcod.Color(r, g, b)
            libtcod.console_set_default_foreground(self.console_dict[con], col)

    def console_set_default_background(self, con, r, g, b):
        if cEngine:
            self.engine.mSetBackgroundColor(con, r, g, b)
        else:
            col = libtcod.Color(r, g, b)
            libtcod.console_set_default_background(self.console_dict[con], col)

    def console_print_frame(self, con, x, y, width, height, clear):
        if cEngine:
            self.engine.mPrintFrame(con, int(x), int(y), int(width), int(height), clear, 1, "NULL")
        else:
            libtcod.console_print_frame(self.console_dict[con], int(x), int(y), int(width), int(height), clear)

    def console_print_rect(self, con, x, y, width, height, fmt):
        if cEngine:
            self.engine.mPrintRect(con, int(x), int(y), int(width), int(height), fmt)
        else:
            libtcod.console_print_rect(self.console_dict[con], int(x), int(y), int(width), int(height), fmt)

    def console_blit(self, conSrc, xSrc, ySrc, wSrc, hSrc, conDest, xDest, yDest, foreAlph=1.0, backAlph=1.0):
        if cEngine:
            self.engine.mBlit(conSrc, conDest, int(xSrc), int(ySrc), int(wSrc), int(hSrc), int(xDest), int(yDest), foreAlph, backAlph)
        else:
            src = self.console_dict[conSrc]
            if conDest == 0:
                dest = self.root
            else:
                dest = self.console_dict[conDest]
            src.blit(dest, int(xDest), int(yDest), int(xSrc), int(ySrc), int(wSrc), int(hSrc), foreAlph, backAlph)

    def console_put_char_ex(self, con, x, y, c, cr, cg, cb, br, bg, bb):
        if cEngine:
            self.engine.mPutCharEx(con, x, y, ord(c), cr, cg, cb, br, bg, bb)
        else:
            fore = libtcod.Color(cr, cg, cb)
            back = libtcod.Color(br, bg, bb)
            libtcod.console_put_char_ex(self.console_dict[con], x, y, c, fore, back)

    def console_set_char(self, con, x, y, c):
        if cEngine:
            self.engine.mSetChar(con, x, y, ord(c))
        else:
            libtcod.console_set_char(self.console_dict[con], x, y, c)

    def console_set_alignment(self, con, align):  # Depreciated. Requires refactor then removal
        if cEngine:
            self.engine.mSetAlignment(con, align)
        else:
            libtcod.console_set_alignment(self.console_dict[con], align)

    def console_print(self, con, x, y, fmt):
        if cEngine:
            self.engine.mPrint(con, int(x), int(y), fmt)
        else:
            libtcod.console_print(self.console_dict[con], int(x), int(y), fmt)

    def console_print_ex(self, con, x, y, flag, alignment, fmt):
        if cEngine:
            self.engine.mPrintEx(con, int(x), int(y), flag, alignment, fmt)
        else:
            libtcod.console_print_ex(self.console_dict[con], x, y, flag, alignment, fmt)

    def console_get_char_background(self, con, x, y):
        if cEngine:
            return(0,0,0)
        else:
            col = libtcod.console_get_char_background(self.console_dict[con], x, y)
            return libtcod.color_get_hsv(col)

    def console_get_char_foreground(self, con, x, y):
        if cEngine:
            return (0,0,0)
        else:
            col = libtcod.console_get_char_foreground(self.console_dict[con], x, y)
            return col

    def image_new(self, x, y):
        if cEngine:
            return self.engine.mCreateImage(x, y)
        else:
            self.image_dict[self.image_id_counter] = libtcod.image.Image(x, y)
            c = self.image_id_counter
            self.image_id_counter += 1
            return c

    def image_load(self, path):
        if cEngine:
            return self.engine.mLoadImage(path)
        else:
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
        if cEngine:
            self.engine.mDestroyImage(img)
        else:
            self.image_dict.pop(img)

    def image_clear(self, i, r, g, b):
        if cEngine:
            self.engine.mImageClear(i, r, g, b)
        else:
            col = libtcod.Color(r, g, b)
            self.image_dict[i].clear(col)

    def image_put_pixel(self, i, x, y, r, g, b):
        if cEngine:
            self.engine.mImagePutPixel(i, x, y, r, g, b)
        else:
            col = libtcod.Color(r, g, b)
            self.image_dict[i].put_pixel(x, y, col)

    def image_get_size(self, i):
        if cEngine:
            w = self.engine.mImageGetWidth(i)
            h = self.engine.mImageGetHeight(i)
            return w, h
        else:
            w = self.image_dict[i].width
            h = self.image_dict[i].height
            return w, h

    def image_get_pixel(self, i, x, y):
        if cEngine:
            r = self.engine.mImageGetR(i, x, y)
            g = self.engine.mImageGetG(i, x, y)
            b = self.engine.mImageGetB(i, x, y)
            return r, g, b
        else:
            return self.image_dict[i].get_pixel(x, y)

    def image_blit(self, i, c, x, y, w=-1, h=-1):
        if cEngine:
            self.engine.mImageBlitRect(i, c, int(x), int(y), w, h)
        else:
            self.image_dict[i].blit(self.console_dict[c], float(x), float(y), libtcod.BKGND_SET, 1.0, 1.0, 0)

    def image_blit_2x(self, i, c, x, y, sx=0, sy=0, w=-1, h=-1):
        if cEngine:
            self.engine.mImageBlit2x(i, c, int(x), int(y), sx, sy, w,  h)
        else:
            self.image_dict[i].blit_2x(self.console_dict[c], x, y, sx, sy, w, h)

    def image_replace(self, image, replacement):
        if cEngine:
            pass
        else:
            self.image_dict[image] = replacement

    def map_init_level(self, sizeX, sizeY):
        if SUBCELL:
            sizeX *= 2
            sizeY *= 2
        self.FOV = libtcod.map_new(sizeX, sizeY)
        for tile in self.mMap:
            # tile.explored = False
            self.map_set_properties(tile.x, tile.y, not tile.blocked, not tile.block_sight)

    def map_add_tile(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        if cEngine:
            if SUBCELL:
                self.engine.mDungeonAddTile(x * 2, y * 2, not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
                self.engine.mDungeonAddTile(x * 2 + 1, y * 2, not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
                self.engine.mDungeonAddTile(x * 2, y * 2 + 1, not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
                self.engine.mDungeonAddTile(x * 2 + 1, y * 2 + 1, not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
            else:
                self.engine.mDungeonAddTile(x, y, not blocked, not block_sight, int(color[0]), int(color[1]), int(color[2]))
        self.mMap.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_add_tile_2x(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap2x.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_set_properties(self, x, y, blocked, block_sight):
        libtcod.map_set_properties(self.FOV, x, y, blocked, block_sight)

    def map_new(self, w, h):
        if cEngine:
            if SUBCELL:
                w *= 2
                h *= 2
            self.engine.mDungeonNewMap(w, h)
            self.engine.mLightmaskInit(w, h)
        else:
            pass

    def map_clear(self):
        self.mMap = []
        self.mMap2x = []
        if cEngine:
            pass
            #self.engine.mDungeonReset()

    def set_fov_map(self, map):
        self.FOV = map

    def get_fov_map(self):
        return self.FOV

    def get_map(self):
        return self.mMap

    def get_map_tile(self, x, y):
        # if SUBCELL:
        #     x *= 2
        #     y *= 2
        return self.mMap[x + y * self.w]

    def get_map_tile_color(self, x, y):
        return self.get_map_tile(x, y).color

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

    def map_blit(self, con):
        if cEngine:
            if SUBCELL:
                self.engine.mDungeonBlit2x(con)

    def map_draw(self, con, x=0, y=0, run_fov=True):
        if cEngine:
            if SUBCELL:
                self.engine.mDungeonRenderStaticMap2x(con, x*2, y*2)
            else:
                self.engine.mDungeonRenderStaticMap(con, x, y)
        else:
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
            self.image_blit(self.map_image, con, 0, 0)

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

    def map_is_in_fov(self, x, y):
        # if SUBCELL:
        #     x *= 2
        #     y *= 2
        return libtcod.map_is_in_fov(self.FOV, x, y)

    def map_compute_fov(self, x, y):
        # if SUBCELL:
        #     x *= 2
        #     y *= 2
        libtcod.map_compute_fov(self.FOV, x, y)

    def map_is_explored(self, x, y):
        try:
            if cEngine:
                if SUBCELL:
                    x *= 2
                    y *= 2

                return self.engine.mDungeonIsExplored(x, y)
            else:
                for tile in self.mMap:
                    if tile.x == x and tile.y == y:
                        return tile.explored
        except Exception(e):
            print(e)

    def map_is_transparent(self, x, y):
        if cEngine:
            # if SUBCELL:
            #     x *= 2
            #     y *= 2
            returnable = (
                self.engine.mDungeonIsExplored(x * 2, y * 2),
                self.engine.mDungeonIsExplored(x * 2 + 1, y * 2),
                self.engine.mDungeonIsExplored(x * 2, y * 2 + 1),
                self.engine.mDungeonIsExplored(x * 2 + 1, y * 2 + 1)
            )
            return returnable
        else:
            pass

    def lightmask_set_ambient(self, ambient):
        if cEngine:
            self.engine.mLightmaskSetAmbient(ambient)
        else:
            self.lightmask.set_ambient(ambient)

    def lightmask_set_size(self, w, h):
        if cEngine:
            pass
            self.engine.mLightmaskInit(w, h)
        else:
            self.lightmask.width = w
            self.lightmask.height = h
            self.lightmask_reset()

    def lightmask_set_opacity_value(self, x, y, o):
        if cEngine:
            pass
        else:
            self.lightmask.set_opacity_value(x, y, o)

    def lightmask_set_persistent_lightmask(self):
        if cEngine:
            pass
        else:
            self.lightmask.set_persistent_lightmask()

    def lightmask_reset(self):
        if cEngine:
            self.engine.mLightmaskReset()
        else:
            self.lightmask.reset()

    def lightmask_add_light(self, x, y, br, radius=10):
        if cEngine:
            r, g, b = 0, 0, 0
            if isinstance(br, float):
                r = int(255 * br)
                g = int(255 * br)
                b = int(255 * br)
            else:
                r = int(br[0] * 255)
                g = int(br[1] * 255)
                b = int(br[2] * 255)
            if SUBCELL:
                x *= 2
                y *= 2
                radius *= 2
            radius += 0.5
            self.engine.mLightmaskAddLight(x, y, r, g, b, radius=radius)
        else:
            self.lightmask.add_light(x, y, br)

    def lightmask_set_intensity(self, i):
        if cEngine:
            pass
        else:
            self.lightmask.set_intensity(i)

    def lightmask_compute(self, map):
        if cEngine:
            self.engine.mLightmaskCompute()
        else:
            self.lightmask.compute_mask(map)

    def lightmask_get_mask_value(self, x, y):
        if cEngine:
            if SUBCELL:  # get the average light of the subpixels
                r1 = self.engine.mLightmaskGetValueR(x * 2, y * 2)
                g1 = self.engine.mLightmaskGetValueG(x * 2, y * 2)
                b1 = self.engine.mLightmaskGetValueB(x * 2, y * 2)

                r2 = self.engine.mLightmaskGetValueR(x * 2 + 1, y * 2)
                g2 = self.engine.mLightmaskGetValueG(x * 2 + 1, y * 2)
                b2 = self.engine.mLightmaskGetValueB(x * 2 + 1, y * 2)

                r3 = self.engine.mLightmaskGetValueR(x * 2, y * 2 + 1)
                g3 = self.engine.mLightmaskGetValueG(x * 2, y * 2 + 1)
                b3 = self.engine.mLightmaskGetValueB(x * 2, y * 2 + 1)

                r4 = self.engine.mLightmaskGetValueR(x * 2 + 1, y * 2 + 1)
                g4 = self.engine.mLightmaskGetValueG(x * 2 + 1, y * 2 + 1)
                b4 = self.engine.mLightmaskGetValueB(x * 2 + 1, y * 2 + 1)
                r = (r1 + r2 + r3 + r4) / 4
                g = (g1 + g2 + g3 + g4) / 4
                b = (b1 + b2 + b3 + b4) / 4
                return r, g, b
            else:
                r = self.engine.mLightmaskGetValueR(x, y)
                g = self.engine.mLightmaskGetValueG(x, y)
                b = self.engine.mLightmaskGetValueB(x, y)
                return r, g, b
        else:
            return self.lightmask.get_mask_value(x, y)

    def particle_explosion(self, num, x, y, r=False, b=False, color=None):
        if SUBCELL:
            x *= 2
            y *= 2
        particle.explosion(num, self.particles, x, y, r, b, color)

    def particle_nova(self, num, x, y, r=False, b=False):
        if SUBCELL:
            x *= 2
            y *= 2
        particle.nova(num, self.particles, x, y, r, b)

    def particle_cone_spray(self, num, ox, oy, dx, dy, r=False, b=False):
        if SUBCELL:
            ox *= 2
            oy *= 2
            dx *= 2
            dy *= 2
        particle.cone_spray(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_cone(self, num, ox, oy, dx, dy, r=False, b=False):
        if SUBCELL:
            ox *= 2
            oy *= 2
            dx *= 2
            dy *= 2
        particle.cone(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_projectile(self, num, ox, oy, dx, dy, r=False, b=False, color=None):
        if SUBCELL:
            ox *= 2
            oy *= 2
            dx *= 2
            dy *= 2
        particle.projectile(num, self.particles, ox, oy, dx, dy, r, b, color)

    def particle_update(self, map=None):
        if len(self.particles) >= 1:
            self.particles[0].update(self)
            if self.particles[0].dead:
                self.particles.remove(self.particles[0])
        for p in range(len(self.particles) - 1, 0, -1):
            self.particles[p].update(self)
            if self.particles[p].dead:
                self.particles.pop(p)


    def particle_draw(self, con, c='*'):
        for p in self.particles:
            p.draw(self)
            #self.console_put_char_ex(con, int(p.x), int(p.y), c, 255, 255, 255, 0, 0, 0)

    def random_set_instance(self, seed=None):
        if seed:
            self.random_instance = libtcod.random.Random(seed=seed)
        else:
            self.random_instance = libtcod.random.Random()

    def random_get_int(self, min, max):
        return libtcod.random_get_int(self.random_instance, min, max)

    def random_get_float(self, min, max):
        return libtcod.random_get_float(self.random_instance, min, max)