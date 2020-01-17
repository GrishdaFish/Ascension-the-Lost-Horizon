__author__ = 'GrishdaFish'

import math
from gEngine.utilities.widget import window_widget, button_widget, text_input_widget
from gEngine.utilities.user_interface import menu

import tcod as libtcod

# 18x9
class SpawningTools(window_widget.WindowWidget):
    def close(self):
        self.deactivate()

    def setup(self):
        self.deactivate()

    def minimize(self):
        self.close()

    def update(self, key, mouse):
        if not self.collapsed and not self.minimized:
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
                            scr = ScrollSpawner(self.gEngine, self.game, 0, 0, 16, 1, "Scroll Spawner")
                            scr.setup()
                            self.gEngine.add_module(scr)
                    elif mousey == 3:
                        potion = menu.color_text(potion, libtcod.green)
                        if mouse.lbutton:
                            pot = PotionSpawner(self.gEngine, self.game, 0, 0, 16, 1, "Potion Spawner")
                            pot.setup()
                            self.gEngine.add_module(pot)
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
    def close(self):
        for button in self.buttons:
            button.close()
        self.gEngine.remove_module(self)

    def setup(self):
        self.pots = self.game.build_objects.potions
        self.list_offset = 0
        self.buttons = []
        w_size = 0
        i = 1
        for object in self.pots:
            if len(object.name) > w_size:
                w_size = len(object.name)
            self.buttons.append(
                button_widget.TextButtonWidget(self, 1, i, object.name, self.game.build_objects.build_potion,
                                           [self.game, self.game.player.x, self.game.player.y, object.name]))
            i += 1
        self.height = len(self.pots) + 2
        self.original_height = self.height
        if w_size > len(self.title):
            self.original_width = w_size + 2
            self.width = w_size + 2
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)

    def update(self, key, mouse):
        returnables = []
        for button in self.buttons:
            returnables.append(button.run(key, mouse))
        for returnable in returnables:
            if returnable:
                returnable.item.pick_up(self.game.player.fighter.inventory, self.game)


class ScrollSpawner(window_widget.WindowWidget):
    def close(self):
        for button in self.buttons:
            button.close()
        self.gEngine.remove_module(self)

    def setup(self):
        self.scrolls = self.game.build_objects.scrolls
        self.list_offset = 0
        self.buttons = []
        w_size = 0
        i = 1
        for object in self.scrolls:
            if len(object.name) > w_size:
                w_size = len(object.name)
            self.buttons.append(
                button_widget.TextButtonWidget(self, 1, i, object.name, self.game.build_objects.build_scroll,
                                           [self.game, self.game.player.x, self.game.player.y, object.name]))
            i += 1
        self.height = len(self.scrolls) + 2
        self.original_height = self.height
        if w_size > len(self.title):
            self.original_width = w_size + 2
            self.width = w_size + 2
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)

    def update(self, key, mouse):
        returnables = []
        for button in self.buttons:
            returnables.append(button.run(key, mouse))
        for returnable in returnables:
            if returnable:
                returnable.item.pick_up(self.game.player.fighter.inventory, self.game)