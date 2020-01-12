__author__ = 'GrishdaFish'
import math
from gEngine.utilities.user_interface import window_widget
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
            if mousey == 1:
                mon = menu.color_text(mon, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 1, mon)

            light = "Light Sources: %d" % len(light_sources)
            if mousey == 2:
                light = menu.color_text(light, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 2, light)

            g = "Gear: %d" % len(gear)
            if mousey == 3:
                g = menu.color_text(g, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 3, g)

            c = "Consumables: %d" % len(consumables)
            if mousey == 4:
                c = menu.color_text(c, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 4, c)

            ambient = "Ambient light level: %f" % self.game.ambient
            if mousey == 5:
                ambient = menu.color_text(ambient, libtcod.green, libtcod.grey)
            self.gEngine.console_print(self.con, 1, 5, ambient)
