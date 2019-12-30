import tcod as libtcod
from game import game
from game import dev_mode
from gEngine.utilities.user_interface.menu import Menus
import os
import sys
from gEngine import gEngine as _gEngine
import time

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
        self.images = []
        count = 2
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '0.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '1.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '2.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '3.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '4.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '5.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '6.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '7.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '8.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '9.png')))
        for x in range(count):
            self.images.append(self.gEngine.image_load( os.path.join(path, 'img', '10.png')))

        self.images_2 = []

        for x in range(count+1):
            self.images_2.append(self.gEngine.image_load( os.path.join(path, 'img', '7.png')))
        for x in range(count+1):
            self.images_2.append(self.gEngine.image_load(os.path.join(path, 'img', '8.png')))
        for x in range(count+1):
            self.images_2.append(self.gEngine.image_load(os.path.join(path, 'img', '9.png')))
        for x in range(count+1):
            self.images_2.append(self.gEngine.image_load(os.path.join(path, 'img', '10.png')))
        self.images_2.reverse()
        self.images_logo = []

        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '0.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '1.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '2.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '3.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '4.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '5.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '6.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '7.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '8.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '9.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '10.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '11.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '12.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '13.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '14.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '15.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '16.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '17.png')))
        #self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '18.png')))
        #self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '19.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '10.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '9.png')))
        self.images_logo.append(self.gEngine.image_load(os.path.join(path, 'img', 'title logo', '8.5.png')))

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
        image_index = 0
        logo_index = 0
        first = True
        intro_done = False
        logo_done = False
        logo_img = None
        letter_index = 0
        studio_name = 'Critical Miss Studios'
        name_done = False
        print_name = ''
        lerp_value = 0.0
        lerp_amount = 0.087

        menu_fade = True
        menu_fade_amount = 0.05
        menu_fade_value = 0.0
        self.gEngine.log_open_block("Main menu running...")
        while not libtcod.console_is_window_closed():
            if not intro_done:
                if image_index > len(self.images)-1:
                    if first:
                        image_index = 0
                        #self.images.reverse()
                        first = False
                    #else:
                        image_index = len(self.images)-1
                        intro_done = True
                        image_index = -1
                img = self.images[image_index]
                image_index += 1
            else:
                if image_index > len(self.images_2)-2:
                    image_index = 0
                    self.images_2.reverse()
                img = self.images_2[image_index]
                image_index += 1

            if not logo_done:
                if not logo_index > len(self.images_logo)-1:
                    logo_img = self.images_logo[logo_index]
                    logo_index += 1
                else:
                    logo_done = True
            else:
                if letter_index < len(studio_name):
                    #letter_index = len(studio_name)
                    print_name += studio_name[letter_index]
                else:
                    name_done = True
                letter_index +=1
            self.gEngine.image_blit_2x(img, 0, 0, 0)
            self.gEngine.image_blit_2x(logo_img, 0, 0, 29)
            r, g, b = libtcod.color_lerp(libtcod.light_flame, libtcod.dark_flame, lerp_value)
            if name_done:
                lerp_value += lerp_amount
                if lerp_value < 0.087:
                    lerp_amount = 0.087
                if lerp_value > 0.913:
                    lerp_amount = -0.087


            self.gEngine.console_set_default_foreground(0, r, g, b)
            self.gEngine.console_print(0, int(self.gEngine.SCREEN_WIDTH / 2 - 11),
                                       int(self.gEngine.SCREEN_HEIGHT -15),
                                       print_name)

            # libtcod.console_credits_render(2, self.gEngine.SCREEN_HEIGHT - 2, True)
            self.gEngine.console_set_default_background(0, 0, 0, 0)
            if intro_done:
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
            if choice == 0:  # play new game
                self.gEngine.log_message('Starting new game')
                self.gEngine.remove_module(self)
                self.gEngine.console_remove_console(self.con)

                self.gEngine.log_close_block()
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
                self.gEnginei.log_close_block()
                return
                # self.dev_mode.run()
                # self.main_menu()
        return True
