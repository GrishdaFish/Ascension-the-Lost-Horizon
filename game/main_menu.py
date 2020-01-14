import tcod as libtcod
from game import game
from game import dev_mode
from game.debug_modules import module_list
from game.debug_modules import dungeon_status
from game.debug_modules import spawning_tool
from game.modules import login_module
from gEngine.utilities.user_interface.menu import Menus
import os
import sys
from gEngine import gEngine as _gEngine
import time

class MainMenu:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.active = True
        self.con = 0  # self.gEngine.console_new(self.gEngine.SCREEN_WIDTH, self.gEngine.SCREEN_HEIGHT)
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        path = os.path.join(path, 'content')
        #path = path.replace('core.exe', '')
        self.img = self.gEngine.image_load(os.path.join(path, 'img', 'menu_background_2.png'))
        self.m_menu = Menus(self.gEngine, int(self.gEngine.SCREEN_HEIGHT / 2 + 22),
                            int(self.gEngine.SCREEN_WIDTH), 24, '',  # TODO: remove magic numbers
                            ['Play a new game', 'Continue last game', 'Options (not working)', 'Quit', 'dev'], #'Discord'],
                            self.con, bg=path)
        self.first = True
        self.m_menu = self.m_menu
        self.m_menu.is_visible = True
        self.intro_done = False
        self.logo_done = False
        self.letter_index = 0
        self.studio_name = 'Critical Miss Studios'
        self.name_done = False
        self.print_name = ''
        self.lerp_value = 0.0
        self.lerp_amount = 0.087

        self.menu_fade = True
        self.menu_fade_amount = 0.05
        self.menu_fade_value = 0.0

    def activate(self):
        self.active = True
        self.first = True
        self.m_menu = self.m_menu
        self.m_menu.is_visible = True
        self.intro_done = False
        self.logo_done = False
        self.letter_index = 0
        self.studio_name = 'Critical Miss Studios'
        self.name_done = False
        self.print_name = ''
        self.lerp_value = 0.0
        self.lerp_amount = 0.087

        self.menu_fade = True
        self.menu_fade_amount = 0.05
        self.menu_fade_value = 0.0

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.m_menu.destroy_menu()
        self.deactivate()

    def run(self, key, mouse):
        if self.first:
            self.gEngine.log_open_block("Main menu running...")
            self.first = False
            login = login_module.LoginMenu(self.gEngine, None, self.gEngine.SCREEN_WIDTH / 4,
                                           self.gEngine.SCREEN_HEIGHT / 4, 25, 7, "Login")
            login.setup()
            self.gEngine.add_module(login)

        self.gEngine.console_clear(self.con)
        self.gEngine.console_clear(0)
        # while not libtcod.console_is_window_closed():
        # key, mouse = self.gEngine.handle_input()
        if not self.intro_done:
            img = "game logo fade"
            self.intro_done = self.gEngine.animation_draw_animation(img, 0, 0, 0)
        else:
            img = "game logo flicker"
            self.gEngine.animation_draw_animation(img, 0, 0, 0)
        if self.logo_done:
            if self.letter_index < len(self.studio_name):
                self.print_name += self.studio_name[self.letter_index]
            else:
                self.name_done = True
            self.letter_index +=1

        self.logo_done = self.gEngine.animation_draw_animation("title logo", 0, 0, 29)

        r, g, b = libtcod.color_lerp(libtcod.light_flame, libtcod.dark_flame, self.lerp_value)
        if self.name_done:
            self.lerp_value += self.lerp_amount
            if self.lerp_value < 0.087:
                self.lerp_amount = 0.087
            if self.lerp_value > 0.913:
                self.lerp_amount = -0.087

        self.gEngine.console_set_default_foreground(0, r, g, b)
        self.gEngine.console_print(0, int(self.gEngine.SCREEN_WIDTH / 2 - 11),
                                   int(self.gEngine.SCREEN_HEIGHT -15),
                                   self.print_name)

        # libtcod.console_credits_render(2, self.gEngine.SCREEN_HEIGHT - 2, True)
        self.gEngine.console_set_default_background(0, 0, 0, 0)
        if self.intro_done:
            if self.menu_fade:
                if self.menu_fade_value < 1.0:
                    self.menu_fade_value += self.menu_fade_amount
                else:
                    # menu_fade_value = 1.0
                    self.menu_fade = False
        if not self.gEngine.get_module_status("LoginMenu"):
            choice = self.m_menu.run(key, mouse, self.menu_fade_value)
            #self.gEngine.console_flush()
            if choice == 0:  # play new game
                self.gEngine.log_message('Starting new game')
                self.gEngine.remove_module(self)
                self.gEngine.console_remove_console(self.con)

                self.gEngine.log_close_block()

                g = game.Game(self.gEngine)
                g.new_game()
                self.gEngine.add_module(g)

                d = dungeon_status.DungeonStatus(self.gEngine, g, 5, 6, self.gEngine.SCREEN_WIDTH / 2, 7, "Dungeon Status")
                self.gEngine.add_module(d)

                spawn_tool = spawning_tool.SpawningTools(self.gEngine, g, 0, 0, 18, 9, "Spawning Tools")
                spawn_tool.setup()
                self.gEngine.add_module(spawn_tool)

                # load this module last
                m = module_list.ModuleList(self.gEngine, g, 0, 0, 15, 5, 'Module List')
                self.gEngine.add_module(m)

                return
                # self.new_game()
                # self.play_game()
                # self.main_menu()
            if choice == 1:  # load game
                self.gEngine.log_message('loading game')
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
                return
                # try:
                # self.load_game()
                # except:
                #    msgbox('\n No saved game to load.\n', 24)
                #    continue
                # self.play_game()
                # self.main_menu()
            if choice == 3:# or choice is None:  # quit. TODO fix for new engine
                self.gEngine.log_message('Quitting game')
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
                return True

            if choice == 4:  # dev mode
                self.gEngine.log_message('Entering Devmode')
                self.gEngine.remove_module(self)
                d = dev_mode.DevMode(self.gEngine)
                self.gEngine.add_module(d)
                self.gEngine.log_close_block()
                return
                    # self.dev_mode.run()
                    # self.main_menu()
                # if choice == 5:
                #     self.gEngine.log_message('Sending to Discord...')
            # return True
