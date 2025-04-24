import tcod as libtcod
from game import game
from game import dev_mode
from gEngine.utilities.user_interface.menu import Menus
import os
import sys
from gEngine import gEngine as _gEngine
import game.input_handler as iph
import time

from game.modules import options_module, help_module
from game.object.effects import Effect


class EscMenu:
    def __init__(self, gEngine, game):
        self.gEngine = gEngine
        self.game = game
        self.active = True
        self.con = 0  # self.gEngine.console_new(self.gEngine.SCREEN_WIDTH, self.gEngine.SCREEN_HEIGHT)
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        #path = os.path.join(path, 'content')
        #path = path.replace('core.exe', '')
        # self.img = self.gEngine.image_load(os.path.join(path, 'img', 'menu_background_2.png'))
        self.m_menu = Menus(self.gEngine, int(self.gEngine.SCREEN_HEIGHT / 2 + 22),
                            int(self.gEngine.SCREEN_WIDTH), 24, 'Game Menu',
                            ['Return to Game', 'Options', 'Help', 'Quit to Menu', 'Quit Game (You can\'t)'],
                            self.con)

    def activate(self):
        self.active = True
        self.game.deactivate()

    def deactivate(self):
        self.active = False
        self.game.activate()

    def on_exit(self):
        self.m_menu.destroy_menu()
        self.deactivate()

    def run(self, key, mouse):
        m_menu = self.m_menu
        m_menu.is_visible = True

        menu_fade_value = 1.0
        self.gEngine.log_open_block("ESC menu running...")
        while not libtcod.console_is_window_closed():
            #if not first:
            key, mouse = self.gEngine.handle_input()
            self.gEngine.console_set_default_background(0, (0, 0, 0))

            choice = m_menu.run(key, mouse, alpha=1.0)
            self.gEngine.console_flush()
            self.gEngine.console_clear(self.con)
            self.gEngine.console_clear(0)
            if choice == 0:
                self.gEngine.log_message('Returning to game')
                self.gEngine.remove_module(self)
                self.gEngine.console_remove_console(self.con)
                self.gEngine.log_close_block()
                self.game.activate()
                return
            if choice == 1:
                self.gEngine.log_message('Loading options')
                option = options_module.OptionsModule(self.gEngine, self.game, 0, 0, 25, 7, "Options")
                option.setup()
                self.gEngine.add_module(option)
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
                return
            if choice == 2:
                self.gEngine.log_message('Loading help')
                help_mod = help_module.HelpModule(self.gEngine, self.game, 0, 0, 25, 7, "Help")
                help_mod.setup()
                self.gEngine.add_module(help_mod)
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
            if choice == 3:
                self.gEngine.log_message('Quit to menu')
                class ShoeHorn():
                    def __init__(self):
                        self.vk = libtcod.KEY_ESCAPE
                k = ShoeHorn()
                result = iph.handle_quit(k, self.game, None)
                if result == 'exit':
                    self.game.return_to_main_menu()
                    self.gEngine.remove_module(self)
                    self.gEngine.log_close_block()
                return
            if choice == 4:
                self.gEngine.log_message('Quit game')
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
                return True
            # if choice == 5:
        return True
