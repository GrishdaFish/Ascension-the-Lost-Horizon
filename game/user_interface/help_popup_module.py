__author__ = 'GrishdaFish'
import math
from gEngine.utilities.widget import window_widget
from gEngine.utilities.user_interface import menu
from gEngine import gEngine
from game.modules import options_module

import tcod as libtcod


class HelpPopup(window_widget.WindowWidget):
    def close(self):
        print("HelpPopupClosed")
        self.deactivate()

    def minimize(self):
        self.close()

    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        #TODO: Set default text colors (may require engine update)
        if not self.collapsed and not self.minimized:
            data = self.gEngine.color_text("Welcome to Ascension: The Lost Horizon!", libtcod.light_grey)
            self.gEngine.console_print(self.con, 1, 1, data)

            version = self.gEngine.color_text(str(gEngine.VERSION), libtcod.red)
            data = self.gEngine.color_text("This game is in very early alpha Version % s" % version, libtcod.light_grey)
            self.gEngine.console_print(self.con, 1, 2, data)

            text1 = self.gEngine.color_text("Use ", libtcod.light_grey)
            text2 = "(%s%s%s%s)"%(self.game.keys.key_north, self.game.keys.key_west, self.game.keys.key_south, self.game.keys.key_east)
            text2 = self.gEngine.color_text(text2, libtcod.light_amber)
            text3 = self.gEngine.color_text(" to move around. For a full list of Keybinds - ", libtcod.light_grey)
            data = text1 + text2 + text3
            self.gEngine.console_print(self.con, 1, 4, data)

            data = self.gEngine.color_text("check options from the main menu", libtcod.light_grey)
            self.gEngine.console_print(self.con, 5, 5, data)

            data = self.gEngine.color_text("All menus can be controlled via the mouse.", libtcod.light_grey)
            self.gEngine.console_print(self.con, 1, 7, data)

            text = self.gEngine.color_text("Walk into shop owners ", libtcod.light_grey)
            text2 = self.gEngine.color_text(" to access their shop", libtcod.light_grey)
            text3 = self.gEngine.color_text("(@)", libtcod.white)
            data = text + text3 + text2
            self.gEngine.console_print(self.con, 1, 9, data)

            text1 = self.gEngine.color_text("Make sure to buy a ", libtcod.light_grey)
            text2 = self.gEngine.color_text("LANTERN", libtcod.Color(255, 159, 0))
            text3 = self.gEngine.color_text(" or ", libtcod.light_grey)
            text4 = self.gEngine.color_text("TORCH", libtcod.Color(255, 63, 0))
            text5 = self.gEngine.color_text(" and equip it -", libtcod.light_grey)
            data = text1 + text2 + text3 + text4 + text5
            self.gEngine.console_print(self.con, 1, 11, data)

            text1 = self.gEngine.color_text("before leaving town.", libtcod.light_grey)
            text2 = self.gEngine.color_text(" (Fizzilips to the left)", libtcod.turquoise)
            data = text1 + text2
            self.gEngine.console_print(self.con, 5, 12, data)

            data = self.gEngine.color_text("Light sources are very important in Ascension!", libtcod.light_grey)
            self.gEngine.console_print(self.con, 5, 13, data)

            text1 = self.gEngine.color_text("Also buy a weapon from ", libtcod.light_grey)
            text2 = self.gEngine.color_text("Johan (up and left), ", libtcod.light_azure)
            data = text1 + text2
            self.gEngine.console_print(self.con, 1, 15, data)

            text1 = self.gEngine.color_text("as well as armor from ", libtcod.light_grey)
            text2 = self.gEngine.color_text("The Helm and Buckler", libtcod.cyan)
            text3 = self.gEngine.color_text(" (up and right)", libtcod.light_grey)
            data = text1 + text2 + text3
            self.gEngine.console_print(self.con, 5, 16, data)

            text1 = self.gEngine.color_text("Make sure to equip your light, weapon, and armors, press ", libtcod.light_grey)
            text2 = self.gEngine.color_text("(%s)" % str(self.game.keys.key_inventory), libtcod.red)
            data = text1 + text2
            self.gEngine.console_print(self.con, 1, 18, data)

            data = self.gEngine.color_text("to open inventory and click items to use them.", libtcod.light_grey)
            self.gEngine.console_print(self.con, 5, 19, data)

            text1 = self.gEngine.color_text("Press ", libtcod.light_grey)
            text2 = self.gEngine.color_text("(%s)" % str(self.game.keys.key_help), libtcod.red)
            text3 = self.gEngine.color_text(" to show this screen again", libtcod.light_grey)
            data = text1 + text2 + text3
            self.gEngine.console_print(self.con, 1, 21, data)

            data = "Click the X to close this window."
            pos = int(self.width /2 ) - int(len(data) / 2)
            self.gEngine.console_print(self.con, pos-1, 28, data)

#TODO: Add 'hyperlink' button widgets for "Keydinds" in line 3