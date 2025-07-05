__author__ = 'GrishdaFish'
from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import check_list_boxes
from gEngine.utilities.widget import button_group
from gEngine.utilities.widget import popups

from game.user_interface.widgets.inventory_support_widgets import *
import tcod as libtcod

class Inventory(window_widget.WindowWidget):
    def __init__(self, gEngine, game=None, x=0, y=0, w=0, h=5, title="", target_console=0, draw_frame=False, owner=None):
        '''
        A widget used for inventory and shop management

        :param gEngine: Active instance of gEngine
        :param game: Active Game instance
        :param x: The starting X position for the widget
        :param y: The Starting Y position for the widget
        :param w: The width of the widget
        :param h: The Height of the widget
        :param title: The title to be displayed
        :param target_console: Console to blit this on top of. Defaults to root
        :param draw_frame: Boolean to toggle drawing the frame and title
        :param owner: The owner if this inventory UI, eg.. Player, an NPC, etc..
        '''
        super().__init__(gEngine, game, x, y, w, h, title, target_console, draw_frame)
        self.owner = owner
        self.buttons = []
        self.widgets = []

        if self.owner.fighter:
            self.is_player = True
            self.setup_player_inventory()
        else:
            self.is_player = False
            self.setup_npc_shop()



    def setup_player_inventory(self):
        """
        Sets up the player inventory screen. Player data and NPC data is fundamentally different in approach and display
        :return:
        """
        weapon_display = WeaponDisplay(self.gEngine, w=self.width/2, parent=self, owner=self.owner)
        self.widgets.append(weapon_display)

        equipment_display = EquipmentDisplay(self.gEngine, w=self.width/2, parent=self, owner=self.owner)
        self.widgets.append(equipment_display)

        compare_examine = CompareExamine(self.gEngine, w=self.width/2,  parent=self, owner=self.owner)
        self.widgets.append(compare_examine)

        inventory_display = InventoryDisplay(self.gEngine, w=self.width/2, h=self.height,x=self.width/2, parent=self, owner=self.owner)
        self.widgets.append(inventory_display)

    def setup_npc_shop(self):
        pass

    def update(self, key, mouse):
        if self.active:
            for widget in self.widgets:
                widget.run(key, mouse)

            for button in self.buttons:
                button.run(key, mouse)
    def close(self):
        self.deactivate()
        self.game.activate()
