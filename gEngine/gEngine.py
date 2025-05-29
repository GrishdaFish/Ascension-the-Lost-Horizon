#Pyton interface for the Horizion engine

# Ignore all of the force casting variables to ints. Python 3 is dumb when you divide odd ints,
#   it will convert to a float, which does not play nice with the engine.
# TODO: remove r, g, b from method calls and accept  tcod color, then grab r, g, b in the engine to simply calls
# TODO: ADD 64 Bit Version of _cEngine.pyd!

import tcod as libtcod
import os
import sys
import numpy as np
import textwrap
import traceback
import struct

RELEASE = False
SUBCELL = True

LOGGING_LEVEL = ""
VERSION = "0.0.1a"

REQ_PY_MAJ = 3
REQ_PY_MIN = 8
REQ_PY = "%i.%i.0" % (REQ_PY_MAJ, REQ_PY_MIN)

PY_BIT = (struct.calcsize("P") * 8)

if int(sys.version[0]) < REQ_PY_MAJ:
    raise Exception("Python Version %s Or higher Required!" % REQ_PY)
if int(sys.version[0]) >= REQ_PY_MAJ and int(sys.version[2]) < REQ_PY_MIN:
    raise Exception("Python Version %s Or higher Required!" % REQ_PY)

if PY_BIT == 32:
    from gEngine import cEngine  # TODO change pyd name to cEngine32.pyd
elif PY_BIT == 64:
    raise ImportError("64 Bit Python Not Supported Yet. Please use 32 Bit Python!")
    # TODO import cEngine64.pyd here when compiled
else:
    raise ImportError("Unrecognized Python Bit type, make sure you are using 32 or 64 bit python 3.8.0 or higher")

# gEngine utilities
from gEngine import particle
from gEngine import lights
from gEngine.utilities import options as _options
from gEngine.utilities import config
from gEngine import tcod_event
from gEngine.animation import animations, splash_screen
from gEngine import custom_font


path = os.path.abspath('.')


def in_rect(x, y, w, h):
    return x < w and y < h


class NetworkDummy:
    def __init__(self):
        pass

    def send_package(self, package):
        pass


class gEngineModule:
    """
    Basic module class to inherit for your modules
    Override update with your logic here
    Override setup or call super()__init__ to define initial variables
    """
    def __init__(self):
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = True

    def update(self, key, mouse):
        pass

    def run(self, key, mouse):
        self.update(key, mouse)

    def close(self):
        self.deactivate()

    def on_exit(self):
        pass


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
        self.release = RELEASE
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

        self.color_dark_wall = libtcod.Color(5, 5, 5)  # was libtcod.darkest_grey
        self.color_light_wall = libtcod.Color(30, 30, 30)  # was 99,99,99
        self.color_dark_ground = libtcod.darker_grey
        self.color_light_ground = libtcod.Color(125, 125, 125)
        self.color_tile_wall = libtcod.Color(177, 177, 177)
        self.color_tile_ground = libtcod.Color(190, 190, 190)

        self.light_sources = []
        self.light_handler = lights.LightHandler(self)
        self.noise = libtcod.noise_new(1, libtcod.NOISE_SIMPLEX)

        # self.lightmask = light_mask.LightMask(self.w, 48)

        self.particles = []
        self.modules = []

        self.key = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.root = None
        # self.logger = logging.log_manager()
        self.engine = None
        self.console_id_counter = 0
        self.image_id_counter = 0
        self.image_dict = {}
        self.console_dict = {}

        self.random_instance = None
        self.random_set_instance()
        self.animation_engine = animations.Animations(self)
        try:
            from gEngine.utilities import network
            self.network = network.NetworkController()
        except ImportError as imp_err:
            print(imp_err)
            print("using networking dummy")
            #self.network = NetworkDummy()

        self.additional_modules = []
        self.modules_to_remove = []
        self.module_adjust_list = []
        self.adjusting = False
        self.player_id = None
        self.zdepth = 0

    def run(self):
        # try:
            while True:
                # start every frame by flushing all of the screen, then grab and parse any input
                self.console_flush()

                # all modules receive and parse the same input Do not call self.handle_input() outside the engine
                # unless you pull program control away from the engine NOT RECOMMENDED. AVOID ANY OTHER WHILE LOOP IF
                # POSSIBLE
                key, mouse = self.handle_input()

                # Add any new modules before the run cycle starts
                if len(self.additional_modules) > 0:
                    for modules in self.additional_modules:
                        self.modules.append(modules)
                    self.additional_modules.clear()

                # run all active modules in our module list
                for module in self.modules:
                    if module.active is True:
                        module.run(key, mouse)

                # then after running, we make any adjustments to the list

                # Adjusting positions of modules in the list, eg. bringing a module to the front (back) of the list
                if len(self.module_adjust_list) > 0:
                    self.modules.clear()
                    for module in self.module_adjust_list:
                        self.modules.append(module)
                    self.module_adjust_list.clear()

                # Removing any module(s) that need to be removed before the next run cycle
                if len(self.modules_to_remove) > 0:
                    if len(self.modules) == 1:
                        self.modules.pop()
                    else:
                        for module in self.modules_to_remove:
                            if module in self.modules:
                                self.modules.remove(module)
                    self.modules_to_remove.clear()
                self.adjusting = False

                """except BaseException as e:
                    if str(e) != "None" and str(e) != "69420":
                        self.log_open_block("*** ERROR ***")
                        self.log_message("%s" % str(e), "error")
                        self.log_open_block("*** TRACEBACK***")
                        tb = traceback.format_exc()
                        tb = tb.splitlines()
                        for line in tb:
                            self.log_message(line,"error")
                        self.log_close_block()
                        self.log_close_block()
                        self.close_engine()"""

    def render_all(self):
        self.console_flush()

    def add_module(self, module):
        self.additional_modules.append(module)

    def remove_module(self, module):
        self.modules_to_remove.append(module)
        module.on_exit()

    def get_module_by_name(self, name):
        for module in self.modules:
            if str(module.__class__.__name__) == name:
                return module
        return None

    def get_module_status(self, name):
        """
        Gets the status of the named module
        :param name: string of the module class name
        :return: the status of the named module, or none if the module is not in the list
        """
        module = self.get_module_by_name(name)
        if module:
            return module.active
        else:
            return None

    def bring_module_to_front(self, module):
        """
        Used for bringing widgets to the front of the game screen
        :param module: the module reference
        :return: Nothing
        """
        if self.adjusting:
            return
        self.adjusting = True
        for m in self.modules:
            if m != module:
                self.module_adjust_list.append(m)
        self.module_adjust_list.append(module)

    def activate_module(self, name):
        """
        Activates a module with the specified name
        :param name: A string of the module class name
        :return: True if a module was activated, otherwise False
        """
        module = self.get_module_by_name(name)
        if module:
            module.activate()
            return True
        return False

    def deactivate_module(self, name):
        """
        Deactivates a module with the specified name
        :param name: A string of the module class name
        :return: True if a module was deactivated, otherwise False
        """
        module = self.get_module_by_name(name)
        if module:
            module.deactivate()
            return True
        return False

    def toggle_module(self, module):
        """
        Toggles the status of a module
        :param module: A reference of a module
        :return:
        """
        module.active = not module.active

    def clear_modules(self):
        """
        Clears the engine of modules. Useful before starting the game to start with a fresh set of modules after intros
        :return:
        """
        self.modules = []
        self.additional_modules = []
        self.module_adjust_list = []
        self.modules_to_remove = []

    def log_open_block(self, message=""):
        """
        Creates a new indentation block in the logger
        :param message: A string containting a message
        :return: Nothing
        """
        if cEngine:
            self.engine.mOpenBlock(message)

    def log_close_block(self):
        """
        Closes the last indentation block
        :return: Nothing
        """
        if cEngine:
            self.engine.mCloseBlock()

    def log_message(self, message, level='info'):
        """
        Sends a message to the logger, using the specified level
        :param message: A string of the message to log
        :param level: the level of the message logged
        :return:
        """
        if cEngine:
            levels = {"info": self.engine.mInfo,
                      "notice": self.engine.mNotice,
                      "error": self.engine.mError,
                      "fatal": self.engine.mFatalError}
            if level in levels:
                levels[level](message)

    def logger_set_level(self, level='debug'):
        pass

    def handle_input(self, key=None, mouse=None, clear=False):
        """
        Only call this module if you pull control from the main engine loop and need keyboard or mouse control
        :param key:
        :param mouse:
        :param clear:
        :return: returns key and mouse data
        """
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
            mouse.cx = self.mouse.cx
            mouse.cy = self.mouse.cy

            for event in tcod_event.get():
                if event.type == 'MOUSEMOTION':
                    mouse.cx = self.mouse.cx = int(event.pixel[0] / 16)
                    mouse.cy = self.mouse.cy = int(event.pixel[1] / 16)

                if event.type == 'MOUSEBUTTONDOWN':
                    mouse.cx = self.mouse.cx = int(event.pixel[0] / 16)
                    mouse.cy = self.mouse.cy = int(event.pixel[1] / 16)

                    if event.button == tcod_event.BUTTON_LEFT:
                        # self.mouse.lbutton = True
                        mouse.lbutton = True
                    if event.button == tcod_event.BUTTON_RIGHT:
                        # self.mouse.rbutton = True
                        mouse.rbutton = True

                if event.type == "MOUSEBUTTONUP":
                    mouse.cx = self.mouse.cx = int(event.pixel[0] / 16)
                    mouse.cy = self.mouse.cy = int(event.pixel[1] / 16)

                    if event.button == tcod_event.BUTTON_LEFT:
                        # self.mouse.lbutton_pressed = True
                        mouse.lbutton_pressed = True

                    if event.button == tcod_event.BUTTON_RIGHT:
                        # self.mouse.rbutton_pressed = True
                        mouse.rbutton_pressed = True

                if event.type == "TEXTINPUT":
                    key.c = ord(event.text)

                if event.type == "KEYDOWN":
                    if event.scancode in key_conv:
                        key.vk = key_conv[event.scancode]

                if event.type == "WINDOWCLOSE":
                    self.close_engine()

            return key, mouse
        else:
            key = libtcod.Key()
            mouse = libtcod.Mouse()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY, key, mouse)
            return key, mouse

    def close_engine(self):
        self.log_message("Closing game")
        self.log_close_block()
        exit(69420) # :D

    def init_root(self):  # Root's id will ALWAYS be 0.
        """
        Initializes the TCOD root console. Call after you create an instance of the engine
        :return:
        """
        custom_font_width = 32
        custom_font_height = 12
        if cEngine:
            self.engine = cEngine.gEngine(self.w, self.h, self.name, self.fs, self.fps, self.engine_options.font, custom_font_width, custom_font_height)
        else:
            self.root = libtcod.console_init_root(self.w, self.h, self.name, self.fs, renderer=libtcod.RENDERER_OPENGL2)
            libtcod.sys_set_fps(self.fps)
            self.console_dict[self.console_id_counter] = self.root
            self.console_id_counter += 1

        self.log_open_block("Python info:")
        self.log_message("%s" % sys.version)
        self.log_message("%i bit." % PY_BIT)
        self.log_close_block()

        self.log_open_block("Loading Engine Animations...")
        p = os.path.abspath('.')
        p = os.path.join(p, 'gEngine', 'animation', 'img', 'animations')
        self.animation_engine.load_animations(p)
        self.log_close_block()

        self.animation_engine.load_animations()
        self.load_custom_font_chars()

        s = splash_screen.SplashScreen(self)
        self.add_module(s)

        # self.map_image = self.image_new(self.w, self.h)
        # self.subcell_map_image = self.image_new(self.w * 2, self.h * 2)
        # self.light_map = self.image_new(self.w, self.h)
        # self.subcell_light_map = self.image_new(self.w * 2, self.h * 2)

    def sys_get_fps(self):
        if cEngine:
            return self.engine.mSysGetFPS()
        else:
            return libtcod.sys_get_fps()

    def sys_save_screenshot(self, path):
        self.engine.mSaveScreenshot(path)

    # @staticmethod
    def console_set_custom_font(self, font_file, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, h=0, v=0):
        if cEngine:
            libtcod.console_set_custom_font(font_file, flags, h, v)
            pass
        else:
            font_file = font_file.replace('core.exe', '')
            libtcod.console_set_custom_font(font_file, flags, h, v)

    def console_new(self, width, height):
        """
        Creates a new console of the specified width and h eight
        :param width: int of the width of the new console
        :param height: int of the height of the new console
        :return: an int of the console number (Not the actual console reference)
        """
        if cEngine:
            return self.engine.mAddConsole(int(width), int(height))
        else:
            self.console_dict[self.console_id_counter] = libtcod.console.Console(int(width), int(height))
            c = self.console_id_counter
            self.console_id_counter += 1
        return c

    def console_set_key_color(self, con, col):
        if cEngine:
            self.engine.mSetKeyColor(con, col[0], col[1], col[2])

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
        return self.console_dict[int(con)]

    def console_clear(self, con=0):
        if cEngine:
            self.engine.mClear(int(con))
        else:
            self.console_dict[con].clear()

    def console_remove_console(self, con):
        if cEngine:
            if con > 0:
                self.engine.mDestroyConsole(int(con))
        else:
            if con > 1:  # so we dont try to delete root
                c = self.console_dict.pop(con)
                libtcod.console_delete(c)

    def console_remove_all(self):
        # self.mConsole = []
        # self.console_dict = {}
        # self.console_id_counter = 0
        # self.console_dict[self.console_id_counter] = self.root
        # self.console_id_counter += 1
        pass

    def console_get_height_rect(self, con, x, y, width, height, fmt):
        if cEngine:
            return self.engine.mGetHeightRect(int(con), int(x), int(y), int(width), int(height), fmt)
        else:
            return libtcod.console_get_height_rect(self.console_dict[con], x, y, width, height, fmt)

    def console_set_default_foreground(self, con, col):
        r, g, b = col
        if cEngine:
            self.engine.mSetForegroundColor(con, int(r), int(g), int(b))
        else:
            libtcod.console_set_default_foreground(self.console_dict[con], col)

    def console_set_default_background(self, con, col):
        r, g, b = col
        if cEngine:
            self.engine.mSetBackgroundColor(con, int(r), int(g), int(b))
        else:
            libtcod.console_set_default_background(self.console_dict[con], col)

    def console_print_frame(self, con, x, y, width, height, clear, title="NULL"):
        if cEngine:
            self.engine.mPrintFrame(con, int(x), int(y), int(width), int(height), clear, 1, title)
        else:
            libtcod.console_print_frame(self.console_dict[con], int(x), int(y), int(width), int(height), clear)

    def console_hline(self, con, x, y, l, f=1):
        self.engine.mHLine(con, int(x), int(y), int(l), f)

    def console_vline(self, con, x, y, l, f=1):
        self.engine.mVLine(con, int(x), int(y), int(l), f)

    def console_print_rect(self, con, x, y, width, height, fmt):
        if cEngine:
            self.engine.mPrintRect(con, int(x), int(y), int(width), int(height), fmt)
        else:
            libtcod.console_print_rect(self.console_dict[con], int(x), int(y), int(width), int(height), fmt)

    def console_blit(self, conSrc, xSrc, ySrc, wSrc, hSrc, conDest, xDest, yDest, foreAlph=1.0, backAlph=1.0):
        if cEngine:
            self.engine.mBlit(conSrc, conDest, int(xSrc), int(ySrc), int(wSrc), int(hSrc), int(xDest), int(yDest), float(foreAlph), float(backAlph))
        else:
            src = self.console_dict[conSrc]
            if conDest == 0:
                dest = self.root
            else:
                dest = self.console_dict[conDest]
            src.blit(dest, int(xDest), int(yDest), int(xSrc), int(ySrc), int(wSrc), int(hSrc), foreAlph, backAlph)

    def console_put_char_ex(self, con, x, y, c, fore, back):
        cr, cg, cb = fore
        br, bg, bb = back
        if cEngine:
            self.engine.mPutCharEx(con, int(x), int(y), ord(c), int(cr), int(cg), int(cb), int(br), int(bg), int(bb))
        else:
            libtcod.console_put_char_ex(self.console_dict[con], x, y, c, fore, back)

    def console_set_char(self, con, x, y, c):
        if cEngine:
            self.engine.mSetChar(con, int(x), int(y), ord(c))
        else:
            libtcod.console_set_char(self.console_dict[con], x, y, c)

    def console_set_alignment(self, con, align):  # Depreciated. Requires refactor then removal
        if cEngine:
            self.engine.mSetAlignment(int(con), align)
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
            return self.engine.mCreateImage(int(x), int(y))
        else:
            self.image_dict[self.image_id_counter] = libtcod.image.Image(x, y)
            c = self.image_id_counter
            self.image_id_counter += 1
            return c

    def image_load(self, _path):
        if cEngine:
            return self.engine.mLoadImage(_path)
        else:
            img = libtcod.image_load(_path)
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
            self.engine.mDestroyImage(int(img))
        else:
            self.image_dict.pop(img)

    def image_clear(self, i, col):
        r, g, b = col
        if cEngine:
            self.engine.mImageClear(int(i), int(r), int(g), int(b))
        else:
            self.image_dict[i].clear(col)

    def image_put_pixel(self, i, x, y, col):
        r, g, b = col
        if cEngine:
            self.engine.mImagePutPixel(int(i), int(x), int(y), int(r), int(g), int(b))
        else:
            self.image_dict[i].put_pixel(x, y, col)

    def image_get_size(self, i):
        if cEngine:
            w = self.engine.mImageGetWidth(int(i))
            h = self.engine.mImageGetHeight(int(i))
            return w, h
        else:
            w = self.image_dict[i].width
            h = self.image_dict[i].height
            return w, h

    def image_get_pixel(self, i, x, y):
        if cEngine:
            r = self.engine.mImageGetR(int(i), int(x), int(y))
            g = self.engine.mImageGetG(int(i), int(x), int(y))
            b = self.engine.mImageGetB(int(i), int(x), int(y))
            return r, g, b
        else:
            return self.image_dict[i].get_pixel(x, y)

    def image_blit(self, i, c, x, y, w=-1, h=-1):
        if cEngine:
            self.engine.mImageBlitRect(i, c, int(x), int(y), int(w), int(h))
        else:
            self.image_dict[i].blit(self.console_dict[c], float(x), float(y), libtcod.BKGND_SET, 1.0, 1.0, 0)

    def image_blit_2x(self, i, c, x, y, sx=0, sy=0, w=-1, h=-1):
        if cEngine:
            self.engine.mImageBlit2x(int(i), int(c), int(x), int(y), int(sx), int(sy), int(w), int(h))
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

    def map_add_tile(self, x=0, y=0, cell=" ", blocked=False, block_sight=False, explored=False, spawn_node=None, color=libtcod.white, opacity=0.0):
        if cEngine:
            if SUBCELL:
                self.engine.mDungeonAddTile(int(x * 2), int(y * 2), not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
                self.engine.mDungeonAddTile(int(x * 2 + 1), int(y * 2), not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
                self.engine.mDungeonAddTile(int(x * 2), int(y * 2 + 1), not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
                self.engine.mDungeonAddTile(int(x * 2 + 1), int(y * 2 + 1), not blocked, not block_sight, int(color[0]), int(color[1]),
                                            int(color[2]))
            else:
                self.engine.mDungeonAddTile(x, y, not blocked, not block_sight, int(color[0]), int(color[1]), int(color[2]))
        self.mMap.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_change_tile_blocking(self, x, y, blocked, block_sight):
        """
        Used for adjusting a single tile without recreating the entire map
        :param x: X position of tile to be changed
        :param y: Y position of the tile to be changed
        :param blocked: New blocking value of the tile
        :param block_sight: New Sight blocking value of the tile to be changed
        :return: Nothing
        """
        self.map_set_properties(x, y, not blocked, not block_sight)
        if cEngine:
            if SUBCELL:
                self.engine.mDungeonChangeTileBlocking(int(x * 2), int(y * 2), not blocked, not block_sight)
                self.engine.mDungeonChangeTileBlocking(int(x * 2 + 1), int(y * 2), not blocked, not block_sight)
                self.engine.mDungeonChangeTileBlocking(int(x * 2), int(y * 2 + 1), not blocked, not block_sight)
                self.engine.mDungeonChangeTileBlocking(int(x * 2 + 1), int(y * 2 + 1), not blocked, not block_sight)
        else:
            pass

    def map_add_tile_2x(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap2x.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_set_properties(self, x, y, blocked, block_sight):
        libtcod.map_set_properties(self.FOV, x, y, blocked, block_sight)

    def map_new(self, w, h):
        if cEngine:
            if SUBCELL:
                w *= 2
                h *= 2
            self.engine.mDungeonNewMap(int(w), int(h))
            self.engine.mLightmaskInit(int(w), int(h))
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
        return self.mMap[int(x + y * self.w)]

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
        x = int(x)
        y = int(y)
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
                self.engine.mDungeonRenderStaticMap2x(con, int(x*2), int(y*2))
            else:
                self.engine.mDungeonRenderStaticMap(con, int(x), int(y))
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

                return self.engine.mDungeonIsExplored(int(x), int(y))
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
                self.engine.mDungeonIsExplored(int(x * 2), int(y * 2)),
                self.engine.mDungeonIsExplored(int(x * 2 + 1), int(y * 2)),
                self.engine.mDungeonIsExplored(int(x * 2), int(y * 2 + 1)),
                self.engine.mDungeonIsExplored(int(x * 2 + 1), int(y * 2 + 1))
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
            self.engine.mLightmaskInit(int(w), int(h))
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
            self.engine.mLightmaskAddLight(int(x), int(y), r, g, b, radius=radius)
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
        x = int(x)
        y = int(y)
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

    def particle_explosion(self, num, x, y, decay=0.055, r=False, b=False, color=None, velocity=1.0, lifetime=1.5, clipping=True, char=None, kill_no_vel=False):
        if SUBCELL:
            x *= 2
            y *= 2
        particle.explosion(num, self.particles, x, y, decay=decay, random_decay=r, bounce=b, color=color, velocity=velocity, lifetime=lifetime, clipping=clipping, char=char, kill_no_vel=kill_no_vel)

    def particle_nova(self, num, x, y, r=False, b=False, kill_no_vel=False):
        if SUBCELL:
            x *= 2
            y *= 2
        particle.nova(num, self.particles, x, y, r, b, kill_no_vel=kill_no_vel)

    def particle_cone_spray(self, num, ox, oy, dx, dy, r=False, b=False, clipping=True, char=None, kill_no_vel=False):
        if SUBCELL:
            ox *= 2
            oy *= 2
            dx *= 2
            dy *= 2
        particle.cone_spray(num, self.particles, ox, oy, dx, dy, r, b, clipping=clipping, char=char, kill_no_vel=kill_no_vel)

    def particle_cone(self, num, ox, oy, dx, dy, r=False, b=False, clipping=True, char=None, kill_no_vel=False):
        if SUBCELL:
            ox *= 2
            oy *= 2
            dx *= 2
            dy *= 2
        particle.cone(num, self.particles, ox, oy, dx, dy, r, b, clipping=clipping, char=char, kill_no_vel=kill_no_vel)

    def particle_projectile(self, num, ox, oy, dx, dy, r=False, b=False, color=None, clipping=True, char=None, kill_no_vel=False):
        if SUBCELL:
            ox *= 2
            oy *= 2
            dx *= 2
            dy *= 2
        particle.projectile(num, self.particles, ox, oy, dx, dy, r, b, color, clipping=clipping, char=char, kill_no_vel=kill_no_vel)

    def particle_clear(self):
        self.particles.clear()

    def particle_update(self, map=None):
        if len(self.particles) >= 1:
            self.particles[0].update(self)
            if self.particles[0].dead:
                self.particles.remove(self.particles[0])
        for p in range(len(self.particles) - 1, 0, -1):
            self.particles[p].update(self)
            if self.particles[p].dead:
                self.particles.pop(p)


    def particle_draw(self, con=None, c='*'):
        # TODO: Add additional Particle array for character particles
        for p in self.particles:
            p.draw(self, con)
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

    def animation_draw_animation(self, name, target, x, y):
        return self.animation_engine.draw_animation(name, target, x, y)

    def network_send_package(self, type, package):
        return self.network.send_package(type, package)

    def load_custom_font_chars(self):
        for name, pos in custom_font.Fonts.items():
            self.engine.mMapAsciiCodeToFont(name, pos[0], pos[1])

    def color_text(self, text, color_f=None, color_b=None):
        # changed to not use color codes, as the items were all colored the same
        # this gives the intended effect
        # txt = text.capitalize()
        txt = text
        rf, gf, bf, rb, gb, bb = 1, 1, 1, 1, 1, 1

        if color_f:
            rf, gf, bf = color_f
            # make sure none of the rgb vlaues are 0
            if rf == 0: rf = 1
            if gf == 0: gf = 1
            if bf == 0: bf = 1
        if color_b:
            rb, gb, bb = color_b
            # make sure none of the rgb vlaues are 0
            if rb == 0: rb = 1
            if gb == 0: gb = 1
            if bb == 0: bb = 1
        # if text is colored and we just need background changed (highlighting)
        # Cant just change the background color here. not working for some stupid reason
        if not color_f and color_b:
            return '%c%c%c%c%s%c' % (libtcod.COLCTRL_BACK_RGB, rb, gb, bb, txt, libtcod.COLCTRL_STOP)
        if color_f and not color_b:
            return '%c%c%c%c%s%c' % (libtcod.COLCTRL_FORE_RGB, rf, gf, bf, txt, libtcod.COLCTRL_STOP)
        if color_f and color_b:
            return "%c%c%c%c%c%c%c%c%s%c" % (libtcod.COLCTRL_FORE_RGB, rf, gf, bf,
                                             libtcod.COLCTRL_BACK_RGB, rb, gb, bb, txt, libtcod.COLCTRL_STOP)

    def light_manager_add_light(self, x, y, duration=0.0, decay=0.0, intensity=0.0, color=None, flicker=False, flicker_intensity=0.025):
        l = lights.Light(x, y, self.light_handler, duration, decay, intensity, color, flicker, flicker_intensity)
        self.light_handler.add_light(l)
        return l

    def light_manager_remove_light(self, light):
        self.light_handler.remove(light)

    def light_manager_update(self):
        self.light_handler.update()

    def light_manager_clear_lights(self):
        self.light_handler.empty()

    def light_manager_render_lights(self):
        self.light_handler.render()