__author__ = 'GrishdaFish'
import math
from gEngine.utilities.widget import window_widget
from gEngine.utilities.user_interface import menu

import tcod as libtcod


class DungeonStatus(window_widget.WindowWidget):
    def update(self, key, mouse):
        if not self.collapsed and not self.minimized:
            mousex = math.ceil(mouse.cx - self.x)
            mousey = math.ceil(mouse.cy - self.y)

            monsters = []
            lights = []
            light_sources = []
            gear = []
            consumables = []
            for object in self.game.objects:
                if object.fighter:
                    monsters.append(object)
                if object.item:
                    if object.item.equipment:
                        if object.item.equipment.torch:
                            light_sources.append(object)
                        else:
                            gear.append(object)
                    else:
                        consumables.append(object)

            mon = "Monsters: %d" % len(monsters)
            if mousey == 1 and 1 <= mousex <= self.width:
                mon = menu.color_text(mon, libtcod.green, libtcod.grey)
                if mouse.lbutton:
                    popup = DungeonStatusPopup(self.gEngine, self.game, 0, 0, 16, 7, title="Monster List")
                    popup.setup(monsters)
                    self.gEngine.add_module(popup)
                if mouse.rbutton:
                    for object in monsters:
                        object.fighter.take_damage(object.fighter.hp, self.game.player, self.game)

            self.gEngine.console_print(self.con, 1, 1, mon)

            light = "Light Sources: %d" % len(light_sources)
            if mousey == 2 and 1 <= mousex <= self.width:
                light = menu.color_text(light, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 2, light)

            g = "Gear: %d" % len(gear)
            if mousey == 3 and 1 <= mousex <= self.width:
                g = menu.color_text(g, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 3, g)

            c = "Consumables: %d" % len(consumables)
            if mousey == 4 and 1 <= mousex <= self.width:
                c = menu.color_text(c, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 4, c)

            ambient = "Ambient light level: %f" % self.game.ambient
            if mousey == 5 and 1 <= mousex <= self.width:
                ambient = menu.color_text(ambient, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 5, ambient)


class DungeonStatusPopup(window_widget.WindowWidget):
    def close(self):
        self.gEngine.remove_module(self)

    def setup(self, data):
        w_size = 0
        for object in data:
            if len(object.name) > w_size:
                w_size = len(object.name)
        if w_size + 2 > self.width:
            self.original_width = w_size + 2
            self.width = w_size + 2
        self.height = 7
        self.original_height = 7

        self.data = data
        self.list_offset = 0
        self.arrow_up = chr(30)
        self.arrow_down = chr(31)
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.original_width, self.original_height)

    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        arrow_up = self.arrow_up
        arrow_down = self.arrow_down
        if mousex == 0:
            if mousey == 1:
                arrow_up = menu.color_text(self.arrow_up, libtcod.green)
                if mouse.lbutton:
                    if self.list_offset > 0:
                        self.list_offset -= 1
            if mousey == 3:
                arrow_down = menu.color_text(self.arrow_down, libtcod.green)
                if mouse.lbutton:
                    if self.list_offset < len(self.data) -1:
                        self.list_offset += 1

        self.gEngine.console_print(self.con, 0, 1, arrow_up)
        self.gEngine.console_print(self.con, 0, 3, arrow_down)
        if len(self.data) > 0:
            end = self.list_offset + 5
            if end > len(self.data) - 1:
                end = len(self.data) - 1
            i = 1
            for index in range(self.list_offset, end):
                data = self.data[index].name
                if mousex >= 1 and mousex <= self.width-1:
                    if mousey == i and not mouse.lbutton:
                        data = menu.color_text(data, libtcod.green)
                    elif mousey == i and mouse.lbutton:
                        data = menu.color_text(data, libtcod.red)
                        if self.data[index].fighter:
                            m = MonsterPopup(self.gEngine, self.game, self.x+self.width + 1, self.y+self.height+1,
                                             22+4, 5, self.data[index].name)
                            m.setup(self.data[index])
                            self.gEngine.add_module(m)
                self.gEngine.console_print(self.con, 1, i, data)
                i += 1


class MonsterPopup(window_widget.WindowWidget):
    def close(self):
        self.gEngine.remove_module(self)
        self.data.force_display = False

    def setup(self, data):
        self.data = data
        self.data.force_display = True

    def update(self, key, mouse):
        # print hp, lclick to heal, rclick to kill
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)

        self.gEngine.console_print(self.con, 1, 1, "LB to Heal, RB to Kill")
        if self.data.fighter:
            data = "Hp: %d" % self.data.fighter.hp
            if mousex >= 1 and mousex <= self.width - 1:
                if mousey == 2:
                    data = menu.color_text(data, libtcod.green)
                    if mouse.lbutton:
                        self.data.fighter.heal(self.data.fighter.stat.get_stat_base("HP"))
                    if mouse.rbutton:
                        self.data.fighter.take_damage(self.data.fighter.hp, self.game.player, self.game)
        else:
            data = "Monster Dead"
        self.gEngine.console_print(self.con, 1, 2, data)


