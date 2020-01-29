__author__ = 'GrishdaFish'

from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import button_group
from gEngine import custom_font
import tcod as libtcod


class PerkScreen(window_widget):
    def setup(self):
        self.perk_tree_buttons = button_group.ButtonGroupWidget(self, 1, 1, 5, 1, True)
        # add buttons for each perk here

    def activate(self):
        pass

    def deactivate(self):
        pass

    def on_exit(self):
        pass

    def update(self):
        pass
