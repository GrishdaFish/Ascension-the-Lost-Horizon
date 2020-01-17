__author__ = 'GrishdaFish'
from gEngine import gEngine as _gEngine
from game import main_menu
import sys
import os
import tcod as libtcod
from game.modules import login_module


class SplashScreen:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.active = True
        self.con = self.gEngine.console_new(self.gEngine.SCREEN_WIDTH, self.gEngine.SCREEN_HEIGHT)
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        path = os.path.join(path, 'content')
        #self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.deactivate()

    def run(self, key, mouse):
        splash_done = False
        splash_index = 0
        console_fade = 1.0
        console_fade_amount = 0.008
        self.gEngine.log_open_block("Splash Screen Running")
        while not libtcod.console_is_window_closed():

            key, mouse = self.gEngine.handle_input()

            if key.vk == libtcod.KEY_SPACE or key.vk == libtcod.KEY_ESCAPE or key.vk == libtcod.KEY_ENTER:
                self.gEngine.log_message("Splash skipped, proceeding to main menu")
                self.gEngine.remove_module(self)
                self.gEngine.console_remove_console(self.con)
                main = main_menu.MainMenu(self.gEngine)
                self.gEngine.add_module(main)
                self.gEngine.log_close_block()
                return

            if console_fade <= 0.0:
                self.gEngine.log_message("Splash done, proceeding to main menu")
                self.gEngine.remove_module(self)
                self.gEngine.console_remove_console(self.con)
                main = main_menu.MainMenu(self.gEngine)
                self.gEngine.add_module(main)

                self.gEngine.log_close_block()
                return

            if splash_done:
                console_fade -= console_fade_amount

            #self.gEngine.image_blit_2x(img, self.con, 0, 0)
            splash_done = self.gEngine.animation_draw_animation("splash screen", self.con, 0, 0)
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, console_fade, console_fade)

            self.gEngine.console_flush()
            self.gEngine.console_clear(0)