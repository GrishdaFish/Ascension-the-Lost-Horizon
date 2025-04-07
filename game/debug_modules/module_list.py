__author__ = 'GrishdaFish'
import math
from gEngine.utilities.widget import window_widget
from gEngine.utilities.user_interface import menu
from game.debug_modules import module_list

import tcod as libtcod


class ModuleList(window_widget.WindowWidget):
    def update(self, key, mouse):
        # dynamic widget setup
        self.height = len(self.gEngine.modules) + 2
        w_size = 0
        for module in self.gEngine.modules:
            if len(str(module.__class__.__name__)) > w_size:
                w_size = len(str(module.__class__.__name__) )
        if w_size + 2 > self.width:
            self.width = w_size + 2
        resize = False
        if self.width != self.original_width:
            self.original_width = w_size + 2
            resize = True
        if self.height != self.original_height:
            self.original_height = len(self.gEngine.modules) + 2
            resize = True
        if resize:
            self.gEngine.console_remove_console(self.con)
            self.con = self.gEngine.console_new(self.width, self.height)

        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        i = 1
        if not self.collapsed and not self.minimized:
            for index in range(len(self.gEngine.modules)):
                data = str(self.gEngine.modules[index].__class__.__name__)
                if 1 <= mousex <= self.width - 1:
                    if mousey == i and not mouse.lbutton:
                        data = menu.color_text(data, libtcod.green)
                    elif mousey == i and mouse.lbutton:
                        data = menu.color_text(data, libtcod.red)
                        self.gEngine.toggle_module(self.gEngine.modules[index])
                        self.gEngine.bring_module_to_front(self.gEngine.modules[index])
                    elif mousey == i and mouse.rbutton:
                        self.gEngine.remove_module(self.gEngine.modules[index])
                if not self.gEngine.modules[index].active:
                    data = menu.color_text(data, libtcod.dark_grey)
                self.gEngine.console_print(self.con, 1, i, data)
                i += 1

