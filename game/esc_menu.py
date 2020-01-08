import tcod as libtcod
from game import game
from game import dev_mode
from gEngine.utilities.user_interface.menu import Menus
import os
import sys
from gEngine import gEngine as _gEngine
import time

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
                            int(self.gEngine.SCREEN_WIDTH), 24, '',  # TODO: remove magic numbers
                            ['Return to Game', 'Options (not working)', 'Quit to Menu', 'Quit Game'],
                            self.con, bg=path)

    def activate(self):
        self.active = True
        self.game.deactivate()
        self.gEngine.console_clear(0)

    def deactivate(self):
        self.active = False
        self.game.activate()

    def on_exit(self):
        self.m_menu.destroy_menu()
        self.deactivate()

    def run(self, key, mouse):
        m_menu = self.m_menu
        m_menu.is_visible = True

        menu_fade = False
        menu_fade_amount = 0.1
        menu_fade_value = 0.0
        self.gEngine.log_open_block("ESC menu running...")
        while not libtcod.console_is_window_closed():
            # if not intro_done:
            #     img = "game logo fade"
            #     intro_done = self.gEngine.animation_draw_animation(img, 0, 0, 0)
            # else:
            #     img = "game logo flicker"
            #     self.gEngine.animation_draw_animation(img, 0, 0, 0)
            # if logo_done:
            #     if letter_index < len(studio_name):
            #         print_name += studio_name[letter_index]
            #     else:
            #         name_done = True
            #     letter_index +=1
            #
            # logo_done = self.gEngine.animation_draw_animation("title logo", 0, 0, 29)
            #
            # r, g, b = libtcod.color_lerp(libtcod.light_flame, libtcod.dark_flame, lerp_value)
            # if name_done:
            #     lerp_value += lerp_amount
            #     if lerp_value < 0.087:
            #         lerp_amount = 0.087
            #     if lerp_value > 0.913:
            #         lerp_amount = -0.087
            #
            #
            # self.gEngine.console_set_default_foreground(0, r, g, b)
            # self.gEngine.console_print(0, int(self.gEngine.SCREEN_WIDTH / 2 - 11),
            #                            int(self.gEngine.SCREEN_HEIGHT -15),
            #                            print_name)
            #
            # # libtcod.console_credits_render(2, self.gEngine.SCREEN_HEIGHT - 2, True)
            # self.gEngine.console_set_default_background(0, 0, 0, 0)
            # if intro_done:
            if menu_fade:
                if menu_fade_value < 1.0:
                    menu_fade_value += menu_fade_amount
                else:
                    # menu_fade_value = 1.0
                    menu_fade = False


            choice = m_menu.run(menu_fade_value)
            self.gEngine.console_flush()
            self.gEngine.console_clear(self.con)
            self.gEngine.console_clear(0)
            if choice == 0:  # return to game
                self.gEngine.log_message('Returning to game')
                self.gEngine.remove_module(self)
                self.gEngine.console_remove_console(self.con)
                self.gEngine.log_close_block()
                # g = game.Game(self.gEngine)
                # g.new_game()
                # self.gEngine.add_module(g)
                return
                # self.new_game()
                # self.play_game()
                # self.main_menu()
            if choice == 1:  # options
                self.gEngine.log_message('Loading options')
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
            if choice == 3:
                self.gEngine.log_message('Quit to menu')
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
                return

            if choice == 4:  # dev mode
                self.gEngine.log_message('Quit game')
                self.gEngine.remove_module(self)
                self.gEngine.log_close_block()
                return True
                # self.dev_mode.run()
                # self.main_menu()
            # if choice == 5:
            #     self.gEngine.log_message('Sending to Discord...')
        return True