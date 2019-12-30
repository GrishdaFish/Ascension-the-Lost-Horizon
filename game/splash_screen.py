__author__ = 'GrishdaFish'
from gEngine import gEngine as _gEngine
from game import main_menu
import sys
import os
import tcod as libtcod

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
        self.animations = []
        self.animations.append(self.gEngine.image_load(
            os.path.join(path, 'img', 'animations', 'splash screen', '0.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '1.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '2.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '3.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '4.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '5.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '6.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '7.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '8.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '9.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '10.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '11.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '12.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '13.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '14.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '15.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '16.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '17.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '18.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '19.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '20.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '21.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '22.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '23.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '24.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '25.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '26.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '27.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '28.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '29.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '30.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '31.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '32.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '33.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '34.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '35.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '36.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '37.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '38.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '39.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '40.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '41.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '42.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '43.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '44.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '45.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '46.png')))
        self.animations.append(
            self.gEngine.image_load(os.path.join(path, 'img', 'animations', 'splash screen', '47.png')))

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
            if splash_index < len(self.animations) - 1:
                img = self.animations[splash_index]
                splash_index += 1
            else:
                img = self.animations[len(self.animations)-1]
                splash_done = True

            if key.vk == libtcod.KEY_SPACE or key.vk == libtcod.KEY_ESCAPE or key.vk == libtcod.KEY_ENTER:
                self.gEngine.log_message("Splash done, proceeding to main menu")
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

            self.gEngine.image_blit_2x(img, self.con, 0, 0)
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, console_fade, console_fade)

            self.gEngine.console_flush()
            self.gEngine.console_clear(0)