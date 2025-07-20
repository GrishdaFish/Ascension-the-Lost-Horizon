__author__ = 'GrishdaFish'
##Pyton interface for the Horizion engine##

##====================================================================================================================##
## Table of Contents
##====================================================================================================================##
"""
Table of Contents
gEngine Packages and contents
Notes
TODO List
Change Log
Imports
Globals
Version Checking
gEngine related imports
Helper functions
Dummy Classes and functions
Helper Classes
gEngine
Internal Engine Functions
System functions
Main Loop
Module functions
Logging functions
Non-Drawing Console functions
Drawing console functions
Image functions
Map/Dungeon/Fov functions
Lightmask/Lightmap functions
Light Manager functions
Particle functions
Random functions
Network functions
Sound functions
Engine Popup Functions
"""

##====================================================================================================================##
## gEngine Packages and contents
##====================================================================================================================##
"""
animations
    animations.py 
        ## Cutscene style animations
    splash_screen.py 
        ## Engine splash screen

modules  ## debug and utility modules
    module_list.py 
        ## Creates a widget that will display all modules in the engine
    
utilities
    timing
        ticker.py ## turn based timing system
        
    user_interface ## mostly depreciated, use widgets instead
        button.py 
            ## Depreciated
        check_box.py 
            ## Depreciated
        dialog_box.py 
            ## Depreciated
        hot_bar.py 
            ## Not depreciated!
        menu.py 
            ## Depreciated
        tab.py 
            ## Depreciated
        
    widget ## UI widgets, see each individual module for more info and usage
        button_group.py
        button_widget.py
        check_list_boxes.py
        panels.py
        popups.py
        text_input_widget.py
        window_widget.py 
            ## This is the main widget
    
    config.py 
        ## loads and parse the engine config file
    console.py 
        ## old tool to embedd the python interpreter in game to modify code during runtime
    dijikstra_map.py 
        ## a basic interpretation of dijikstra maps - _very slow_
    load_options.py 
        ## function for loading game options
    messaging.py 
        ## UI class for drawing messages for the player to read in game
    network.py 
        ## old networking controller - unused currently
    options.py 
        ## loads the game options file
    status_bar.py 
        ## for colored visual UI elements like HP/Mana/XP bars
    vector.py 
        ## some vector math utility functions
    xp_loader.py 
        ## for loading REXPaint files - unused currently
        
custom_font.py 
    ## handling for custom font chars via the tileset.png
light_mask.py 
    ## deprecated, will remove in the future
lights.py 
    ## Light object and Light Handler for the lighting system
particle.py 
    ## particle object, and particle functions

tcod_event.py 
    ## slight custom logic for mouse handling via tcod events

_cEngine.pyd  
    ## the c++ engine compiled down
cEngine.py 
    ## The python interface to the _cEngine.pyd

config.toml 
    ## The Engine config file
engine_changelog  
    ## Not very accurate!
libtcod.dll 
    ## This is the dll version used by the C++ TCOD version (Currently 1.15, might upgrade to 1.19)
SDL2.dll 
    ## This is the dll version used by the C++ TCOD version (Currently 1.15, might upgrade to 1.19)

"""
##====================================================================================================================##
## Notes
##====================================================================================================================##
"""
Ignore all of the force casting variables to ints. Python 3 is dumb when you divide odd ints,
    it will convert to a float, which does not play nice with the engine.
    
"""
##====================================================================================================================##
## TODO LIST
##====================================================================================================================##
# TODO: ADD 64 Bit Version of _cEngine.pyd!
# TODO: Clean up unused functions - Started
# TODO: Add missing docstrings - Started
# TODO: add libtcod constants to this engine to avoid depreciation warnings from future libtcod versions
# TODO: Add libtcod.Random() functions wrapped here - Started
# TODO: Add in type hinting - Started
# TODO: Change all c++ engine logging to log from here instead

##====================================================================================================================##
## Change Log
##====================================================================================================================##
"""
7/4/2025 - Added doc strings, table of contents, visual function block separators
7/6/2025 - Started adding in type hinting. Removed non cEngine legacy code. Finished logging logic. 
                Added additional logging.
7/11/2025 - Started adding sound support. Needs c++ engine support
7/13/2025 - Added engine popup functions
7/15/2025 - Added debug specific logging level, debug will also print the debug message. Replace most prints with debug
                logging, so release distributions don't have as many prints

"""

##====================================================================================================================##
## Imports
##====================================================================================================================##
import tcod as libtcod
import os
import sys
import numpy as np
import traceback
import struct
import time
import inspect

##====================================================================================================================##
## Globals
##====================================================================================================================##
RELEASE: bool = False
SUBCELL: bool = True

INFO: str = "info"
DEBUG: str = "debug"
NOTICE: str = "notice"
ERROR: str = "error"
FATAL: str = "fatal"
LOGGING_LEVEL: str = DEBUG

VERSION: str = "0.0.1a"

REQ_PY_MAJ: int = 3
REQ_PY_MIN: int = 8
REQ_PY: str = "%i.%i.0" % (REQ_PY_MAJ, REQ_PY_MIN)

PY_BIT: int = (struct.calcsize("P") * 8)

ROOT_PATH: str = os.path.abspath('.')

##====================================================================================================================##
## Version Checking
##====================================================================================================================##
if int(sys.version[0]) < REQ_PY_MAJ:
    raise Exception("Python Version %s Or higher Required!" % REQ_PY)
if int(sys.version[0]) >= REQ_PY_MAJ and int(sys.version[2]) < REQ_PY_MIN:
    raise Exception("Python Version %s Or higher Required!" % REQ_PY)

if PY_BIT == 32:
    try:
        from gEngine import cEngine  # TODO change pyd name to cEngine32.pyd
    except ImportError:
        raise ImportError("cEngine.py import failed! Make sure it is in the gEngine folder along side cEngine.pyd")
elif PY_BIT == 64:
    raise ImportError("64 Bit Python Not Supported Yet. Please use 32 Bit Python!")
    # TODO import cEngine64.pyd here when compiled
else:
    raise ImportError("Unrecognized Python Bit type, make sure you are using 32 or 64 bit python 3.8.0 or higher")

##====================================================================================================================##
## gEngine related imports
##====================================================================================================================##
from gEngine import particle
from gEngine import lights
from gEngine.utilities.widget import popups
from gEngine.utilities import options as _options
from gEngine.utilities import config
from gEngine import tcod_event
from gEngine.animation import animations, splash_screen
from gEngine import custom_font

##====================================================================================================================##
## Helper Functions
##====================================================================================================================##
def in_rect(x: int, y: int, w: int, h: int) -> bool:
    """
    Checks to see if x, y is inside a rectangle defined by w,h
    :param x: x location to be checked
    :param y: y location to be checked
    :param w: value x to be checked against
    :param h: value y to be checked against
    :return: True if its inside, False otherwise
    """
    return x < w and y < h

##====================================================================================================================##
## Dummy classes and functions
##====================================================================================================================##
class NetworkDummy:
    """
    Dummy class for testing networking functions
    """
    def __init__(self):
        pass

    def send_package(self, package: object) -> None:
        pass

##====================================================================================================================##
## Helper Classes
##====================================================================================================================##

class gEngineModule:
    """
    Basic module class to inherit for your modules
    Override update with your logic here
    Override setup or call super().__init__ to define initial variables
    """
    def __init__(self) -> None:
        self.active: bool = False

    def on_exit(self) -> None:
        """
        Internal function to cleanup this object
        :return: None
        """
        self.close()
        self.deactivate()
    def activate(self) -> None:
        """
        Activates the module
        :return: None
        """
        self.active: bool = True

    def deactivate(self) -> None:
        """
        Deactivates the module
        :return: None
        """
        self.active = False

    def update(self, key: any, mouse: any) -> None:
        """
        Override this function to perform custom behavior
        :param key: libtcod.Key() object
        :param mouse: libtcod.Mouse() object
        :return: None
        """
        pass

    def run(self, key: any, mouse: any) -> None:
        """
        Internal function that runs the module
        :param key: libtcod.Key() object
        :param mouse: libtcod.Mouse() object
        :return: None
        """
        self.update(key, mouse)

    def close(self) -> None:
        """
        Override this function to provide custom exit behavior
        :return:
        """
        self.deactivate()

    def setup(self) -> None:
        """
        Override this to set up initial state of the module if you don't want to super().__init__()
        :return:
        """
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

class EngineAlert(popups.Alert):
    """
    Slightly customized Alert popup for engine popup messages
    """
    def close(self):
        self.active=False
        self.gEngine.reactivate_modules()
        self.gEngine.remove_module(self)
        self.ok_button.close()

##====================================================================================================================##
## gEngine
##====================================================================================================================##
class gEngine:
    """
    The main python interface for the Horizon Engine. Handles all drawing, images, animations, particles, sound

    Interfaces with the C++ engine via cEngine.py->cEngine.pyd
    """
    def __init__(self):
        self.release: bool = RELEASE
        self.engine_options: any = config.EngineConfig()
        self.options: any = _options.GameOptions()
        self.options.load_options()
        self.custom_font_options: any = custom_font.CustomFontOptions()

        self.fonts: dict = {}
        self.w: int = self.engine_options.screen_width
        self.h: int = self.engine_options.screen_height
        self.SCREEN_WIDTH: int = self.w
        self.SCREEN_HEIGHT: int = self.h

        self.name = self.engine_options.name + ' ' + self.engine_options.version
        self.fs = self.options.fullscreen
        self.fps = self.options.fps
        #self.fps = 60

        self.frame_duration = 1 / self.fps

        self.console_set_custom_font(self.engine_options.font,
                                     self.engine_options.font_layout |
                                     self.engine_options.font_type)

        self.mConsole: list = []
        self.mMap: list = []
        self.mMap2x: list = []
        self.mImages: list = []
        self.FOV: any = None

        self.color_dark_wall: any = libtcod.Color(5, 5, 5)  # was libtcod.darkest_grey
        self.color_light_wall: any = libtcod.Color(30, 30, 30)  # was 99,99,99
        self.color_dark_ground: any = libtcod.darker_grey
        self.color_light_ground: any = libtcod.Color(125, 125, 125)
        self.color_tile_wall: any = libtcod.Color(177, 177, 177)
        self.color_tile_ground: any = libtcod.Color(190, 190, 190)

        self.light_sources: list = []
        self.light_handler: any = lights.LightHandler(self)
        self.noise: any = libtcod.noise_new(1, libtcod.NOISE_SIMPLEX)

        # self.lightmask = light_mask.LightMask(self.w, 48)

        self.particles: list = []
        self.modules: list = []

        self.key: any = libtcod.Key()
        self.mouse: any = libtcod.Mouse()
        self.root: any = None
        # self.logger = logging.log_manager()
        self.engine: any = None
        self.console_id_counter: int = 0
        self.image_id_counter: int = 0
        self.image_dict: dict = {}
        self.console_dict: dict = {}

        self.random_instance: any = None
        self.random_set_instance()
        self.animation_engine: any = animations.Animations(self)
        try:
            from gEngine.utilities import network
            self.network: any = network.NetworkController()
        except ImportError as imp_err:
            print(imp_err)
            print("using networking dummy")
            self.network: any = NetworkDummy()

        self.additional_modules: list = []
        self.modules_to_remove: list = []
        self.module_adjust_list: list = []
        self.active_module_list: list = []
        self.adjusting: bool = False
        self.player_id: any = None
        self.zdepth: int = 0

        self.logging_level: dict = {}
        self.logging_defaults: dict = {}
        self.logging_history: list = []

        self.current_music: any = None
        self.music_dict: dict = {}
        self.sfx_dict: dict = {}
        self.music_volume: float = 1.0
        self.sfx_volume: float = 0.5
        self.ui_volume: float = 0.5

    ##================================================================================================================##
    ## Internal Engine Functions
    ##================================================================================================================##
    def init_root(self, pre_init_logging: list = None) -> None:  # Root's id will ALWAYS be 0.
        """
        Initializes the TCOD root console. Call after you create an instance of the engine
        Also finishes initializing the rest of the engine that __init__ doesn't do
        :return: None
        """
        custom_font_width: int = self.custom_font_options.file_width
        custom_font_height: int = self.custom_font_options.file_height

        self.engine = cEngine.gEngine(self.w, self.h, self.name, self.fs, 0, self.engine_options.font,
                                      custom_font_width, custom_font_height)

        self.logging_defaults = {
            "debug": self.engine.mInfo,
            "info": self.engine.mInfo,
            "notice": self.engine.mNotice,
            "error": self.engine.mError,
            "fatal": self.engine.mFatalError
        }
        self.logger_set_level(LOGGING_LEVEL)
        if pre_init_logging:
            self.log_open_block("Pre-init logging messages", override=True)
            for log in pre_init_logging:
                self.log_message(log, override=True)

        self.log_open_block("Python info:", override=True)
        self.log_message("%s" % sys.version, override=True)
        self.log_message("%i bit." % PY_BIT, override=True)
        self.log_close_block(override=True)

        self.log_open_block("Init Audio...", override=True)

        self.load_music()
        self.load_sfx()
        #mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        #mixer.init()
        #pygame.init()
        self.log_message(str(self.music_dict), DEBUG)
        self.log_message((str(self.sfx_dict)), DEBUG)
        self.sound_play_music('djen')
        self.sound_play_sfx('ui_click')
        self.log_message("...Done!", INFO, override=True)
        self.log_close_block(override=True)

        self.log_open_block("Loading Engine Animations...")
        p = os.path.abspath('.')
        p = os.path.join(p, 'gEngine', 'animation', 'img', 'animations')
        self.animation_engine.load_animations(p)
        self.log_close_block()

        self.animation_engine.load_animations()
        self.load_custom_font_chars()


        s = splash_screen.SplashScreen(self)
        self.add_module(s)

    def handle_input(self, key: any=None, mouse: any=None, clear: bool=False) -> tuple:
        """
        Only call this module if you pull control from the main engine loop and need keyboard or mouse control
        :param key:
        :param mouse:
        :param clear:
        :return: returns key and mouse data
        """
        key_conv: dict = {
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
                key: any = libtcod.Key()
            if not mouse or clear:
                mouse: any = libtcod.Mouse()
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

    def close_engine(self, exit_code: int=69420) -> None:
        """
        Closes the engine and performs any necessary actions
        :param exit_code:
        :return: Nothing
        """
        self.log_message("Closing game", NOTICE, True)
        self.log_close_block()
        exit(exit_code)  # :D

    def load_custom_font_chars(self) -> None:
        """
        Loads all custom font from custom_font.toml
        :return: Nothing
        """
        for font in self.custom_font_options.fonts:
            self.fonts.update({font.name:font.id})
            self.engine.mMapAsciiCodeToFont(font.id, font.location[0], font.location[1])

    def load_music(self):
        music_path = os.path.join(ROOT_PATH, 'content', 'sound', 'music')
        self.log_open_block("Loading music in [%s]" % music_path, INFO, True)
        for root, dirs, files in os.walk(music_path):
            if len(files) > 0:
                for file in files:
                    value = os.path.join(root, file)
                    key = os.path.splitext(os.path.basename(file))
                    self.music_dict[key[0]] = value
                    self.log_message("Loading music file [%s]"% value, INFO, True)
        self.log_close_block(INFO, True)

    def load_sfx(self):
        sfx_path = os.path.join(ROOT_PATH, 'content', 'sound', 'sfx')
        self.log_open_block("Loading sfx in [%s]" % sfx_path, INFO, True)
        for root, dirs, files in os.walk(sfx_path):
            if len(files) > 0:
                for file in files:
                    value = os.path.join(root, file)
                    key = os.path.splitext(os.path.basename(file))
                    self.sfx_dict[key[0]] = value
                    self.log_message("Loading sfx file [%s]" % value, INFO, True)
        self.log_close_block(INFO, True)


    ##================================================================================================================##
    ## System related functions
    ##================================================================================================================##
    def sys_get_fps(self) -> int:
        """
        Returns the current FPS
        :return: Fps
        """
        return self.engine.mSysGetFPS()

    def sys_save_screenshot(self, path: str) -> None:
        """
        Saves a screen shot to the supplied path
        :param path: Path to save a screen shot
        :return: None
        """
        self.engine.mSaveScreenshot(path)

    # @staticmethod
    def console_set_custom_font(self, font_file, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, h=0, v=0):
        libtcod.console_set_custom_font(font_file, flags, h, v)

    ##================================================================================================================##
    ## Main Loop
    ##================================================================================================================##
    def run(self) -> None:
        """
        This is the main game loop while using the engine, where all of the modules are executed
        Active modules in the module list are ran using their run(key,mouse) function. Deactivated modules are
        essentially paused. Do not pull control away from this loop unless you know what you're doing or the engine
        will not work properly.

        Each module will have key and mouse input passed to it from the handle_input function

        Do not modify modules from the engine manually, instead use the appropriate functions instead:
            add_module
            remove_module
            get_module
            bring_module_to_front
            clear_moodules

        The following functions are useful if you don't have a direct reference to a module, but you have the class name:
            activate_module
            deactivate_module
            toggle_module

        Other useful module functions:
            get_module_status
            deactivate_all_modules
            reactivate_modules

        :return:
        """
        try:
            while True:
                frame_time = time.time()
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

                elapsed_time = time.time() - frame_time
                if elapsed_time < self.frame_duration:
                    time.sleep(self.frame_duration - elapsed_time)

        except BaseException as e:
            if str(e) != "None" and str(e) != "69420":
                self.log_open_block("==========================[ERROR HISTORY OUTPUT BELOW]==========================", override=True)
                for log in self.logging_history:
                    self.log_message(log, override=True, ignore_log=True)
                self.log_close_block("==========================[ERROR HISTORY OUTPUT END]============================", override=True)
                self.log_open_block("*** ERROR ***", override=True)
                self.log_message("%s" % str(e), "error", override=True)
                self.log_open_block("*** TRACEBACK ***", override=True)
                tb = traceback.format_exc()
                tb = tb.splitlines()
                for line in tb:
                    self.log_message(line,"error", override=True)
                    print(line)
                self.log_close_block(override=True)
                self.log_close_block(override=True)
                self.close_engine()

    def render_all(self) -> None:
        self.console_flush()

    ##================================================================================================================##
    ## Module related functions
    ##================================================================================================================##
    def add_module(self, module: any) -> None:
        """
        prepares a module to be added to the engine
        :param module: a module object to be added to the engine. Must be a class and have the following methods:
            run(key, mouse)
            activate()
            deactivate()
        :return: Nothing
        """
        if not callable(getattr(module, "run", None)):
            raise NameError("%s module does not have the required run(key, mouse) method!"% module)
        if not callable(getattr(module,"activate", None)):
            raise NameError("%s module does not have the required activate() method!"% module)
        if not callable(getattr(module,"deactivate", None)):
            raise NameError("%s module does not have the required deactivate() method!"% module)
        if not hasattr(module, "active"):
            raise TypeError("%s module does not have the required bool type: active!" % module)

        self.log_message("Adding module %s" % module.__class__.__name__, DEBUG)
        self.additional_modules.append(module)


    def remove_module(self, module) -> bool:
        """
        Schedules a module to be removed from the engine
        :param module: __name__ of the module, or the module object its self
        :return: True if the module was found and is ready to be removed, False otherwise
        """
        module = self.get_module(module)
        if module:
            self.log_message("Removing module %s."%module.__class__.__name__, DEBUG)
            self.modules_to_remove.append(module)
            module.on_exit()
            return True
        else:
            self.log_message("Supplied module not found! Returning False...", NOTICE)
            return False


    def get_module(self, name) -> any:
        """
        Returns a module if it exists
        :param name: __name__ of the module, or the module object its self
        :return: The module if it exists, or None
        """
        if isinstance(name, str):
            module = self.get_module_by_name(name)
            self.log_message("Getting module %s"% module.__class__.__name__, DEBUG)
            return module
        else:
            if name in self.modules:
                self.log_message("Getting module %s" % name.__class__.__name__, DEBUG)
                return name
            else:
                self.log_message("Supplied module not found! Returning None...", NOTICE)
                return None


    def get_module_by_name(self, name) -> any:
        """
        Returns a module from self.modules, if it exists, using __name__
        :param name: __name__ of the module
        :return: The module if it exists, or None
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string!")

        for module in self.modules:
            if str(module.__class__.__name__) == name:
                return module
        return None


    def get_module_status(self, name)-> any:
        """
        Gets the status of the named module
        :param name: __name__ of the module, or the module object its self
        :return: the status of the named module, or none if the module is not in the list
        """
        module = self.get_module(name)
        if module:
            return module.active
        else:
            return None


    def bring_module_to_front(self, name) -> None:
        """
        Used for bringing widgets to the front of the game screen
        :param name: __name__ of the module, or the module object its self
        :return: Nothing
        """
        module = self.get_module(name)
        if self.adjusting:
            return
        self.adjusting = True
        for m in self.modules:
            if m != module:
                self.module_adjust_list.append(m)
        self.module_adjust_list.append(module)

    def activate_module(self, name)-> bool:
        """
        Activates the named module
        :param name: __name__ of the module, or the module object its self
        :return: True if a module was activated, otherwise False
        """
        module = self.get_module(name)
        if module:
            module.activate()
            return True
        return False

    def deactivate_module(self, name) -> bool:
        """
        Deactivates a module with the specified name
        :param name: __name__ of the module, or the module object its self
        :return: True if a module was deactivated, otherwise False
        """
        module = self.get_module(name)
        if module:
            module.deactivate()
            return True
        return False

    def toggle_module(self, name) -> bool:
        """
        Toggles the status of a module
        :param name: __name__ of the module, or the module object its self
        :return: True if module exists, False otherwise
        """
        module = self.get_module(name)
        if module:
            module.active = not module.active
            return True
        return False

    def clear_modules(self) -> None:
        """
        Clears the engine of modules. Useful before starting the game to start with a fresh set of modules after intros
        :return:
        """
        self.modules: list = []
        self.additional_modules: list = []
        self.module_adjust_list: list = []
        self.modules_to_remove: list = []

    def deactivate_all_modules(self)->None:
        """
        Deactivates and remembers all active modules, essentially a pause command
        :return: None
        """
        for module in self.modules:
            if module.active:
                module.deactivate()
                self.active_module_list.append(module)

    def reactivate_modules(self)->None:
        """
        Reactivates all previously deactivated modules from the above deactivate_all_modules, essentially an unpause command
        :return: None
        """
        for module in self.active_module_list:
            module.activate()
        self.active_module_list = []

    ##================================================================================================================##
    ## Logging related functions
    ##================================================================================================================##
    def log_open_block(self, message: str="", level: str=INFO, override: bool=False) -> None:
        """
        Creates a new indentation block in the logger
        :param message: A string containing a message
        :param level: the level of the message logged
        :param override: whether to override logging level restrictions
        :return: Nothing
        """

        if level in self.logging_level or override:
            if level == "debug":
                message = "[DEBUG] -> %s" %message
                print(message)
            self.engine.mOpenBlock(message)
        else:
            self.logging_history.append("[HISTORY][OPEN BLOCK] %s" % message)

    def log_close_block(self, level: str=INFO, override: bool=False) -> None:
        """
        Closes the latest indentation block
        :param level: the level of the message logged
        :param override: whether to override logging level restrictions
        :return: Nothing
        """
        if level in self.logging_level or override:
            self.engine.mCloseBlock()
        else:
            self.logging_history.append("[HISTORY][CLOSE BLOCK]")

    def log_message(self, message: str, level: str=INFO, override: bool=False, ignore_log: bool=False) -> None:
        """
        Sends a message to the logger, using the specified level
        :param message: A string of the message to log
        :param level: the level of the message logged
        :param override: whether to override logging level restrictions
        :return: Nothing
        """

        if level in self.logging_level:
            if level == "debug":
                message = "[DEBUG] -> %s" % message
                print(message)
            self.logging_level[level](message)
            return
        else:
            if not ignore_log:
                self.logging_history.append("[HISTORY] %s" % message)
        if override:
            self.logging_defaults[level](message)

    def logger_set_level(self, level: str=DEBUG) -> None:
        """
        Sets the minimum required level of logging to be output, debug/info = all
        :param level:
        :return:
        """
        global LOGGING_LEVEL
        LOGGING_LEVEL = level
        LOGGING_LEVEL = LOGGING_LEVEL.lower()
        default = ["debug",' ', '', None]

        if LOGGING_LEVEL in default:
            self.logging_level = {
                "debug": self.engine.mInfo,
                "info": self.engine.mInfo,
                "notice": self.engine.mNotice,
                "error": self.engine.mError,
                "fatal": self.engine.mFatalError
            }
        elif LOGGING_LEVEL == "info":
            self.logging_level = {
                "info": self.engine.mInfo,
                "notice": self.engine.mNotice,
                "error": self.engine.mError,
                "fatal": self.engine.mFatalError
            }
        elif LOGGING_LEVEL == "notice":
            self.logging_level = {
                "notice": self.engine.mNotice,
                "error": self.engine.mError,
                "fatal": self.engine.mFatalError
            }
        elif LOGGING_LEVEL == "error":
            self.logging_level = {
                "error": self.engine.mError,
                "fatal": self.engine.mFatalError
            }
        else:
            self.logging_level = {
                "fatal": self.engine.mFatalError
            }


    ##================================================================================================================##
    ## Non-Drawing Console related functions
    ##================================================================================================================##
    def console_new(self, width, height) -> int:
        """
        Creates a new console of the specified width and h eight
        :param width: int of the width of the new console
        :param height: int of the height of the new console
        :return: an int of the console number (Not the actual console reference)
        """
        id = self.engine.mAddConsole(int(width), int(height))
        self.log_open_block("Creating a new console...", DEBUG)
        self.log_message("Width [%d], Height [%d], ID [%d]" %(width, height, id), DEBUG)
        self.log_close_block(DEBUG)
        return id


    def console_set_key_color(self, con, col) -> None:
        self.engine.mSetKeyColor(con, col[0], col[1], col[2])

    def console_flush(self) -> None:
        self.engine.mFlush()

    def console_clear_all(self) -> None:
        pass

    def console_get_console(self, con: int) -> any:
        return self.console_dict[int(con)]

    def console_clear(self, con: int=0) -> None:
        self.engine.mClear(int(con))

    def console_remove_console(self, con: int) -> bool:
        self.log_open_block("Removing console...", DEBUG)
        if con > 0:
            self.log_message("Removing console [%d]" % con, DEBUG)
            success = self.engine.mDestroyConsole(int(con))
            if success:
                self.log_message("Console [%d] removed successfully" % con, DEBUG)
            else:
                self.log_message("Removing console [%d] failed! Check to see if console exists!" % con, ERROR)
                #TODO: Add a c++ check function maybe?
            self.log_close_block(DEBUG)
        else:
            self.log_open_block("Error removing console!", ERROR)
            self.log_message("Cannot remove root (con=0) console!", ERROR)
            success = False
            self.log_close_block(ERROR)
        return success

    def console_remove_all(self) -> None:
        # self.mConsole = []
        # self.console_dict = {}
        # self.console_id_counter = 0
        # self.console_dict[self.console_id_counter] = self.root
        # self.console_id_counter += 1
        pass

    ##================================================================================================================##
    ## Drawing console functions
    ## See libtcod documentation for more info on these functions
    ##================================================================================================================##
    def console_get_height_rect(self, con: int, x: int, y: int, width: int, height: int, fmt: str)->any:
        return self.engine.mGetHeightRect(int(con), int(x), int(y), int(width), int(height), fmt)

    def console_set_default_foreground(self, con: int, col: tuple)->None:
        r, g, b = col
        self.engine.mSetForegroundColor(con, int(r), int(g), int(b))

    def console_set_default_background(self, con: int, col: tuple)->None:
        r, g, b = col
        self.engine.mSetBackgroundColor(con, int(r), int(g), int(b))

    def console_print_frame(self, con: int, x: int, y: int, width: int, height: int, clear: bool, title:str ="NULL")->None:
        self.engine.mPrintFrame(con, int(x), int(y), int(width), int(height), clear, 1, title)

    def console_hline(self, con: int, x: int, y: int, l: int, f: int=1)->None:
        self.engine.mHLine(con, int(x), int(y), int(l), f)

    def console_vline(self, con: int, x: int, y: int, l: int, f: int=1)->None:
        self.engine.mVLine(con, int(x), int(y), int(l), f)

    def console_print_rect(self, con: int, x: int, y: int, width: int, height: int, fmt: str)->None:
        self.engine.mPrintRect(con, int(x), int(y), int(width), int(height), fmt)

    def console_blit(self, conSrc: int, xSrc: int, ySrc: int, wSrc: int, hSrc: int, conDest: int, xDest: int, yDest: int, foreAlph: float=1.0, backAlph: float=1.0)->None:
        self.engine.mBlit(conSrc, conDest, int(xSrc), int(ySrc), int(wSrc), int(hSrc), int(xDest), int(yDest), float(foreAlph), float(backAlph))

    def console_put_char_ex(self, con: int, x: int, y: int, c: str, fore:tuple, back:tuple)->None:
        """
        Sets the destination cell to the specified color and character. Automatically converts to custom fonts if
            len(c) > 1
        :param con: destination console
        :param x: x position of the char
        :param y: y position of the char
        :param c: the character to be displayed, will automatically convert a custom_font string
        :param fore: the foreground color
        :param back: the background color
        :return: nothing
        """
        cr, cg, cb = fore
        br, bg, bb = back
        self.engine.mPutCharEx(con, int(x), int(y), ord(self.get_char(c)), int(cr), int(cg), int(cb), int(br), int(bg), int(bb))

    def console_set_char(self, con: int, x: int, y: int, c: str)->None:
        self.engine.mSetChar(con, int(x), int(y), ord(self.get_char(c)))

    def console_set_alignment(self, con, align):  # Depreciated. Requires refactor then removal
        self.engine.mSetAlignment(int(con), align)

    def console_print(self, con: int, x: int, y: int, fmt: str)->None:
        self.engine.mPrint(con, int(x), int(y), fmt)

    def console_print_ex(self, con: int, x: int, y: int, flag: int, alignment: int, fmt: str)->None:
        self.engine.mPrintEx(con, int(x), int(y), flag, alignment, fmt)

    def console_get_char_background(self, con, x, y):
        return(0,0,0)

    def console_get_char_foreground(self, con, x, y):
        return (0,0,0)

    ##================================================================================================================##
    ## Image functions
    ## See libtcod documentation for more info on these functions
    ##================================================================================================================##
    def image_new(self, width, height):
        self.log_open_block("Creating a new TCODImage...", DEBUG)
        id = self.engine.mCreateImage(int(width), int(height))
        self.log_message("Width [%d], Height [%d], ID [%d]" % (width, height, id), DEBUG)
        self.log_close_block(DEBUG)
        return id


    def image_load(self, _path):
        return self.engine.mLoadImage(_path)

    def image_delete(self, img):
        self.engine.mDestroyImage(int(img))

    def image_clear(self, i, col):
        r, g, b = col
        self.engine.mImageClear(int(i), int(r), int(g), int(b))

    def image_put_pixel(self, i, x, y, col):
        r, g, b = col
        self.engine.mImagePutPixel(int(i), int(x), int(y), int(r), int(g), int(b))

    def image_get_size(self, i):
        w = self.engine.mImageGetWidth(int(i))
        h = self.engine.mImageGetHeight(int(i))
        return w, h

    def image_get_pixel(self, i, x, y):
        r = self.engine.mImageGetR(int(i), int(x), int(y))
        g = self.engine.mImageGetG(int(i), int(x), int(y))
        b = self.engine.mImageGetB(int(i), int(x), int(y))
        return r, g, b

    def image_blit(self, i, c, x, y, w=-1, h=-1):
        self.engine.mImageBlitRect(i, c, int(x), int(y), int(w), int(h))

    def image_blit_2x(self, i, c, x, y, sx=0, sy=0, w=-1, h=-1):
        self.engine.mImageBlit2x(int(i), int(c), int(x), int(y), int(sx), int(sy), int(w), int(h))

    def image_replace(self, image, replacement):
        pass

    ##================================================================================================================##
    ## Map/Dungeon/Fov functions
    ##================================================================================================================##
    def map_init_level(self, sizeX, sizeY):
        if SUBCELL:
            sizeX *= 2
            sizeY *= 2
        self.FOV = libtcod.map_new(sizeX, sizeY)
        for tile in self.mMap:
            # tile.explored = False
            self.map_set_properties(tile.x, tile.y, not tile.blocked, not tile.block_sight)

    def map_add_tile(self, x=0, y=0, cell=" ", blocked=False, block_sight=False, explored=False, spawn_node=None, color=libtcod.white, opacity=0.0):
        if SUBCELL:
            self.engine.mDungeonAddTile(int(x * 2), int(y * 2), not blocked, not block_sight, int(color[0]),
                                        int(color[1]), int(color[2]))
            self.engine.mDungeonAddTile(int(x * 2 + 1), int(y * 2), not blocked, not block_sight, int(color[0]),
                                        int(color[1]), int(color[2]))
            self.engine.mDungeonAddTile(int(x * 2), int(y * 2 + 1), not blocked, not block_sight, int(color[0]),
                                        int(color[1]), int(color[2]))
            self.engine.mDungeonAddTile(int(x * 2 + 1), int(y * 2 + 1), not blocked, not block_sight, int(color[0]),
                                        int(color[1]), int(color[2]))
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
        if SUBCELL:
            self.engine.mDungeonChangeTileBlocking(int(x * 2), int(y * 2), not blocked, not block_sight)
            self.engine.mDungeonChangeTileBlocking(int(x * 2 + 1), int(y * 2), not blocked, not block_sight)
            self.engine.mDungeonChangeTileBlocking(int(x * 2), int(y * 2 + 1), not blocked, not block_sight)
            self.engine.mDungeonChangeTileBlocking(int(x * 2 + 1), int(y * 2 + 1), not blocked, not block_sight)

    def map_add_tile_2x(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap2x.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_set_properties(self, x, y, blocked, block_sight):
        libtcod.map_set_properties(self.FOV, x, y, blocked, block_sight)

    def map_new(self, w, h):
        if SUBCELL:
            w *= 2
            h *= 2
        self.engine.mDungeonNewMap(int(w), int(h))
        self.engine.mLightmaskInit(int(w), int(h))

    def map_clear(self):
        self.mMap = []
        self.mMap2x = []
        pass

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
        if SUBCELL:
            self.engine.mDungeonBlit2x(con)

    def map_draw(self, con, x=0, y=0, run_fov=True):
        if SUBCELL:
            self.engine.mDungeonRenderStaticMap2x(con, int(x*2), int(y*2))
        else:
            self.engine.mDungeonRenderStaticMap(con, int(x), int(y))

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
        if SUBCELL:
            x *= 2
            y *= 2

        return self.engine.mDungeonIsExplored(int(x), int(y))

    def map_is_transparent(self, x: int, y: int)->any:
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

    ##================================================================================================================##
    ## Lightmask/Lightmap functions
    ##================================================================================================================##
    def lightmask_set_ambient(self, ambient: float):
        self.engine.mLightmaskSetAmbient(ambient)

    def lightmask_set_size(self, w, h):
        self.engine.mLightmaskInit(int(w), int(h))

    def lightmask_set_opacity_value(self, x, y, o):
        pass

    def lightmask_set_persistent_lightmask(self):
        pass

    def lightmask_reset(self):
        self.engine.mLightmaskReset()

    def lightmask_add_light(self, x, y, br, radius=10):
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

    def lightmask_set_intensity(self, i):
        pass

    def lightmask_compute(self, map):
        self.engine.mLightmaskCompute()

    def lightmask_get_mask_value(self, x, y):
        x = int(x)
        y = int(y)
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


    ##================================================================================================================##
    ## Light Manager functions
    ##================================================================================================================##
    def light_manager_add_light(self, x, y, duration=0.0, decay=0.0, intensity=0.0, color=None, flicker=False,
                                flicker_intensity=0.025):
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
    ##================================================================================================================##
    ## Particle functions
    ##================================================================================================================##
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

    ##================================================================================================================##
    ## Random functions
    ##================================================================================================================##
    def random_set_instance(self, seed=None):
        if seed:
            self.random_instance = libtcod.random.Random(seed=seed)
        else:
            self.random_instance = libtcod.random.Random()

    def random_get_int(self, min, max):
        return libtcod.random_get_int(self.random_instance, min, max)

    def random_get_float(self, min, max):
        return libtcod.random_get_float(self.random_instance, min, max)

    ##================================================================================================================##
    ## Animation functions
    ##================================================================================================================##
    def animation_draw_animation(self, name, target, x, y):
        return self.animation_engine.draw_animation(name, target, x, y)

    def animation_clear_cell(self):
        self.animation_engine.clear_cell_animations()

    def animation_clear_cell_ui(self):
        self.animation_clear_cell_ui()

    def animation_remove_cell(self, cell):
        self.animation_engine.remove_cell_animation(cell)

    def animation_remove_cell_ui(self, cell):
        self.animation_engine.remove_cell_ui_animation(cell)

    def animation_add_cell_animation(self, con, frames=None, loop=False, x=0, y=0, color=libtcod.white, delay=5, fore=True):
        a = animations.CellAnimation(self, con, frames, loop, x, y, color, delay, fore)
        self.animation_engine.add_cell_animation(a)
        return a

    def animation_add_cell_ui_animation(self, con, frames=None, loop=False, x=0, y=0, color=libtcod.white, delay=5, fore=True):
        a = animations.CellAnimation(self, con, frames, loop, x, y, color, delay, fore)
        self.animation_engine.add_cell_ui_animation(a)
        return a

    def animation_draw_animations_back(self, map=True):
        self.animation_engine.draw_cell_animations_back(map)

    def animation_draw_animations_fore(self, map=True):
        self.animation_engine.draw_cell_animations_fore(map)

    def animation_draw_ui(self):
        self.animation_engine.draw_cell_ui_animation()

    ##================================================================================================================##
    ## Network functions
    ##================================================================================================================##
    def network_send_package(self, type, package):
        pass
        #return self.network.send_package(type, package)

    ##================================================================================================================##
    ## Sound functions
    ##================================================================================================================##
    def sound_play_music(self, music: str = "")->any:
        """
        Plays a music file
        :param music: either the name contained in self.music_dict or the path to the file. If a path is supplied
            then it will be added to the dict using the file's name without the extension
        :return: the pygame.mixer.Sound() object created
        """
        if music in self.music_dict.keys():
            #sound = mixer.Sound(self.music_dict[music])
            #sound.set_volume(self.music_volume)
            self.log_message("playing %s music file!" % music, DEBUG)
        else:
            pass
            '''sound = mixer.Sound(music)
            sound.set_volume(self.music_volume)
            sound.play()
            key = os.path.splitext(os.path.basename(music))
            self.music_dict[key[0]] = music'''
        return #sound

    def sound_play_sfx(self, sfx: str = "")->any:
        if sfx in self.sfx_dict.keys():
            self.log_message("Playing %s sfx" % self.sfx_dict[sfx], DEBUG)
            #sound = mixer.Sound(self.sfx_dict[sfx])
            #sound.set_volume(self.sfx_volume)
        else:
            pass
            #sound = mixer.Sound(sfx)
            #sound.set_volume(self.sfx_volume)
            #sound.play()
            #key = os.path.splitext(os.path.basename(sfx))
            #self.music_dict[key[0]] = sfx
        return #sound

    ##================================================================================================================##
    ## Engine Popups functions
    ##================================================================================================================##
    def engine_debug_popup(self, title: str, message: str, override: bool=False) -> None:
        """
        An alert popup that needs no game information. Pops up in the middle of the screen and pauses all modules
        Unpauses modules on ok click. Only pops up on RELEASE == False or override == True
        :param title: The title to be displayed on the popup
        :param message: The body message of the popup
        :param override: whether to override logging level restrictions
        :return: None
        """
        if not RELEASE or override:
            title = "DEBUG - " + title
            self.log_open_block("Debug popup - Title: %s" % title, DEBUG, override)
            self.log_message(message, DEBUG, override)
            self.deactivate_all_modules()
            alert =EngineAlert(self, x=self.w/2, y=self.h/2, title=title)
            alert.setup(message)
            alert.x = self.w/2 - alert.width/2
            alert.y = self.h/2 - alert.height/2
            self.add_module(alert)
            self.log_close_block(DEBUG, override)

    def engine_info_popup(self, title: str, message: str, override: bool=False) -> None:
        """
        An alert popup that needs no game information. Pops up in the middle of the screen and pauses all modules
        Unpauses modules on ok click. Respects logging levels
        :param title: The title to be displayed on the popup
        :param message: The body message of the popup
        :param override: whether to override logging level restrictions
        :return: None
        """
        if INFO in self.logging_level or override:
            title = "INFO - " + title
            self.log_open_block("Info popup - Title: %s" % title, INFO, override)
            self.log_message(message, INFO, override)
            self.deactivate_all_modules()
            alert = EngineAlert(self, x=self.w / 2, y=self.h / 2, title=title)
            alert.setup(message)
            alert.x = self.w / 2 - alert.width / 2
            alert.y = self.h / 2 - alert.height / 2
            self.add_module(alert)
            self.log_close_block(INFO, override)

    def engine_notice_popup(self, title: str, message: str, override: bool=False) -> None:
        """
        An alert popup that needs no game information. Pops up in the middle of the screen and pauses all modules
        Unpauses modules on ok click. Respects logging levels
        :param title: The title to be displayed on the popup
        :param message: The body message of the popup
        :param override: whether to override logging level restrictions
        :return: None
        """
        if NOTICE in self.logging_level or override:
            title = "NOTICE - " + title
            self.log_open_block("Notice popup - Title: %s" % title, NOTICE, override)
            self.log_message(message, NOTICE, override)
            self.deactivate_all_modules()
            alert = EngineAlert(self, x=self.w / 2, y=self.h / 2, title=title)
            alert.setup(message)
            alert.x = self.w / 2 - alert.width / 2
            alert.y = self.h / 2 - alert.height / 2
            self.add_module(alert)
            self.log_close_block(NOTICE, override)

    def engine_error_popup(self, title: str, message: str, override: bool=False) -> None:
        """
        An alert popup that needs no game information. Pops up in the middle of the screen and pauses all modules
        Unpauses modules on ok click. Respects logging levels
        :param title: The title to be displayed on the popup
        :param message: The body message of the popup
        :param override: whether to override logging level restrictions
        :return: None
        """
        if ERROR in self.logging_level or override:
            title = "ERROR - " + title
            self.log_open_block("Error popup - Title: %s" % title, ERROR, override)
            self.log_message(message, ERROR, override)
            self.deactivate_all_modules()
            alert = EngineAlert(self, x=self.w / 2, y=self.h / 2, title=title)
            alert.setup(message)
            alert.x = self.w / 2 - alert.width / 2
            alert.y = self.h / 2 - alert.height / 2
            self.add_module(alert)
            self.log_close_block(ERROR, override)

    def engine_fatal_popup(self, title: str, message: str, override: bool=False) -> None:
        """
        An alert popup that needs no game information. Pops up in the middle of the screen and pauses all modules
        Unpauses modules on ok click. Always pops up as Fatal Errors are always available in logging
        :param title: The title to be displayed on the popup
        :param message: The body message of the popup
        :param override: whether to override logging level restrictions
        :return: None
        """
        title = "FATAL - " + title
        self.log_open_block("Fatal popup - Title: %s" % title, FATAL, override)
        self.log_message(message, FATAL, override)
        self.deactivate_all_modules()
        alert = EngineAlert(self, x=self.w / 2, y=self.h / 2, title=title)
        alert.setup(message)
        alert.x = self.w / 2 - alert.width / 2
        alert.y = self.h / 2 - alert.height / 2
        self.add_module(alert)
        self.log_close_block(FATAL, override)

    ##================================================================================================================##
    ## Internal helper functions
    ##================================================================================================================##
    def get_char(self, c: str)->chr:
        """
        Checks supplied char or string
        :param c: char or string to check for custom character
        :return: either the original char or custom char based on provided string
        """
        if len(c) > 1:
            return chr(self.fonts[c])
        else: return c

    def clamp_float(self, f: float, l: int=1)->float:
        """
        clamps a float to 2 decimal places
        :param f:
        :param l:
        :return:
        """
        return f - f % 1e-2

    def color_text(self, text: str, color_f: tuple = None, color_b: tuple = None) -> str:
        """
        Applies libtcod COLORCTRL codes to color text for libtcod
        :param text: The text to be colored, string
        :param color_f: The foreground color, can be libtcod.Color, or a 3 element tuple (R, G, B)
        :param color_b:  The background color, can be libtcod.Color, or a 3 element tuple (R, G, B)
        :return: the string complete with proper color control codes
        """
        txt = text
        rf, gf, bf, rb, gb, bb = 1, 1, 1, 1, 1, 1

        if color_f:
            rf, gf, bf = color_f
            # make sure none of the rgb values are 0
            if rf == 0: rf = 1
            if gf == 0: gf = 1
            if bf == 0: bf = 1
        if color_b:
            rb, gb, bb = color_b
            # make sure none of the rgb values are 0
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
                                             libtcod.COLCTRL_BACK_RGB, rb, gb, bb,
                                             txt, libtcod.COLCTRL_STOP)