import tcod as libtcod
from game import game
from game import dev_mode
from gEngine.utilities.user_interface.menu import Menus
import os
import sys
from gEngine import gEngine as _gEngine

class MainMenu:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.active = True
        self.con = self.gEngine.console_new(self.gEngine.SCREEN_WIDTH, self.gEngine.SCREEN_HEIGHT)
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        path = os.path.join(path, 'content')
        #path = path.replace('core.exe', '')
        self.img = self.gEngine.image_load(os.path.join(path, 'img', 'menu_background_2.png'))
        self.m_menu = Menus(self.gEngine, int(self.gEngine.SCREEN_HEIGHT / 2 + 22),
                            int(self.gEngine.SCREEN_WIDTH), 24, '',  # TODO: remove magic numbers
                            ['Play a new game', 'Continue last game', 'Options (not working)', 'Quit', 'dev'],
                            self.con, bg=path)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.m_menu.destroy_menu()
        self.deactivate()

    def run(self, key, mouse):
        img = self.img
        m_menu = self.m_menu
        m_menu.is_visible = True
        # m_menu.can_drag = False

        while not libtcod.console_is_window_closed():
            self.gEngine.image_blit_2x(img, 0, 0, 0)

            r, g, b = libtcod.red
            self.gEngine.console_set_default_foreground(0, r, g, b)
            self.gEngine.console_print(0, int(self.gEngine.SCREEN_WIDTH / 2 - 13),
                                       int(self.gEngine.SCREEN_HEIGHT / 2 - 10),
                                       'By Critical Miss Studios')

            libtcod.console_credits_render(2, self.gEngine.SCREEN_HEIGHT - 2, True)
            self.gEngine.console_set_default_background(0, 0, 0, 0)
            choice = m_menu.run()
            self.gEngine.console_flush()
            self.gEngine.console_clear(self.con)
            self.gEngine.console_clear(0)
            if choice == 0:  # play new game
                self.gEngine.log_message('Starting new game')
                self.gEngine.remove_module(self)
                g = game.Game(self.gEngine)
                g.new_game()
                self.gEngine.add_module(g)

                return
                # self.new_game()
                # self.play_game()
                # self.main_menu()
            if choice == 1:  # load game
                self.gEngine.log_message('loading game')
                self.gEngine.remove_module(self)
                return
                # try:
                # self.load_game()
                # except:
                #    msgbox('\n No saved game to load.\n', 24)
                #    continue
                # self.play_game()
                # self.main_menu()
            if choice == 3 or choice is None:  # quit. TODO fix for new engine
                self.gEngine.log_message('Quitting game')
                self.gEngine.remove_module(self)

                return True

            if choice == 4:  # dev mode
                self.gEngine.log_message('Entering Devmode')
                self.gEngine.remove_module(self)
                d = dev_mode.DevMode(self.gEngine)
                self.gEngine.add_module(d)
                return
                # self.dev_mode.run()
                # self.main_menu()
        return True
