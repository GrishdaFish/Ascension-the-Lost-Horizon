__author__ = 'GrishdaFish'

import math
from gEngine.utilities.user_interface import window_widget
from gEngine.utilities.user_interface import menu

import tcod as libtcod


class LoginMenu(window_widget.WindowWidget):
    def setup(self):
        self.user_name = ''
        self.password = ''
        self.in_user = False
        self.in_pass = False

    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)

