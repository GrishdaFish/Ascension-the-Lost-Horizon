__author__ = 'GrishdaFish'

import math
from gEngine.utilities.user_interface import window_widget
from gEngine.utilities.user_interface import menu

import tcod as libtcod

# 18x9
class SpawningTools(window_widget.WindowWidget):
    def setup(self):
        self.deactivate()


    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)

        mon = "Spawn Monster"
        scroll = "Spawn Scroll"
        potion = "Spawn Potion"
        gear = "Spawn Gear"
        full_set = "Spawn Full Set"
        move_up = "Move to up"
        move_down = "Move to down"

        # TODO NOTE idgaf about this if chain. sux my d, its a debugging tool
        if self.mouse_is_in_console(mouse):
            if 1 <= mousex <= self.width - 1:
                if mousey == 1:
                    mon = menu.color_text(mon, libtcod.green)
                    if mouse.lbutton:
                        pass
                elif mousey == 2:
                    scroll = menu.color_text(scroll, libtcod.green)
                    if mouse.lbutton:
                        pass
                elif mousey == 3:
                    potion = menu.color_text(potion, libtcod.green)
                    if mouse.lbutton:
                        pass
                elif mousey == 4:
                    gear = menu.color_text(gear, libtcod.green)
                    if mouse.lbutton:
                        pass
                elif mousey == 5:
                    full_set = menu.color_text(full_set, libtcod.green)
                    if mouse.lbutton:
                        pass
                elif mousey == 6:
                    move_up = menu.color_text(move_up, libtcod.green)
                    if mouse.lbutton:
                        pass
                elif mousey == 7:
                    move_down = menu.color_text(move_down, libtcod.green)
        self.gEngine.console_print(self.con, 1, 1, mon)
        self.gEngine.console_print(self.con, 1, 2, scroll)
        self.gEngine.console_print(self.con, 1, 3, potion)
        self.gEngine.console_print(self.con, 1, 4, gear)
        self.gEngine.console_print(self.con, 1, 5, full_set)
        self.gEngine.console_print(self.con, 1, 6, move_up)
        self.gEngine.console_print(self.con, 1, 7, move_down)


class PotionSpawner(window_widget.WindowWidget):
    def setup(self):
        self.pots = self.game.build_objects.potions
        self.list_offset = 0
        w_size = 0
        for object in self.pots:
            if len(object.name) > w_size:
                w_size = len(object.name)
        self.original_width = w_size + 2
        self.width = w_size + 2

    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        i = 1

        # for index in range(self., end):
        #     data = self.data[index].name
        #     if mousex >= 1 and mousex <= self.width - 1:
        #         if mousey == i and not mouse.lbutton:
        #             data = menu.color_text(data, libtcod.green)
        #         elif mousey == i and mouse.lbutton:
        #             data = menu.color_text(data, libtcod.red)
        #             if self.data[index].fighter:
        #                 m = MonsterPopup(self.gEngine, self.game, self.x + self.width + 1, self.y + self.height + 1,
        #                                  22 + 4, 5, self.data[index].name)
        #                 m.setup(self.data[index])
        #                 self.gEngine.add_module(m)
        #     self.gEngine.console_print(self.con, 1, i, data)
        #     i += 1