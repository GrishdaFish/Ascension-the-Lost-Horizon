__author__ = 'GrishdaFish'
from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import check_list_boxes
from gEngine.utilities.widget import button_group
from gEngine.utilities.widget import popups
from gEngine.utilities.widget import panels

import tcod as libtcod

class WeaponDisplay(panels.StaticPanel):
    def __init__(self, gEngine, parent, owner, x=0, y=0, w=0, h=8, title="Weapons", draw_frame=True):
        '''
        A widget used for displaying Weapon Info for the Player Inventory

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
        super().__init__(gEngine, parent, x, y, w, h, title, draw_frame)
        self.owner = owner


class InventoryDisplay(panels.StaticPanel):
    def __init__(self, gEngine, parent, owner, x=0, y=0, w=0, h=0, title="Inventory", draw_frame=True):
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
        super().__init__(gEngine, parent, x, y, w, h, title, draw_frame)
        self.owner = owner
        self.buttons = []

        self.exit_button = button_widget.ButtonWidget(self, self.w - 8, self.h - 1, 'Exit', self.parent.close)
        self.buttons.append(self.exit_button)
    def check_for_overlap(self):
        pass

    def update(self, key, mouse):
        if self.parent.is_active():
            for button in self.buttons:
                button.run(key, mouse)

class EquipmentDisplay(panels.StaticPanel):
    def __init__(self, gEngine, parent, owner, x=0, y=8, w=0, h=14, title="Equipment", draw_frame=True):
        '''
        A widget used for displaying Equipment Info for the Player Inventory

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
        super().__init__(gEngine, parent, x, y, w, h, title, draw_frame)
        self.owner = owner
        self.equipment_slots = []
        self.buttons = []

        # Set up initial data
        self.display_data = {
            "Head":      "Head      : ",
            "Shoulders": "Shoulders : ",
            "Arms":      "Arms      : ",
            "Hands":     "Hands     : ",
            "Torso":     "Torso     : ",
            "Legs":      "Legs      : ",
            "Feet":      "Feet      : ",
            "Cloak":     "Cloak     : ",
            "Neck":      "Neck      : ",
            "Ring":      "Ring      : ",
        }
        i=1
        for item in self.owner.fighter.gear.equipped:
            if not item == "1h" and not item == "2h":
                if self.owner.fighter.gear.equipped[item]:
                    equip = self.owner.fighter.gear.equipped[item]
                    b = EquipmentDataButton(self, 13, i, equip.name, None, None, item, equip.color)
                    self.buttons.append(b)
                else:
                    equip = "Empty"
                    b = EquipmentDataButton(self, 13, i, equip, None, None, item, libtcod.dark_grey)
                    self.buttons.append(b)
                i+=1
    def setup(self, data):
        self.equipment_slots = self.owner.fighter.gimmie_da_slots()

    def update(self, key, mouse):
        # TODO note because im going to bed, turn all of these slots into buttons for ezpz highlighting
        self.draw_static_data()
        for button in self.buttons:
            button.run(key, mouse)

    def update_data(self, data):
        self.data = data

    def draw_static_data(self):
        i=1
        for line in self.display_data:
            self.gEngine.console_print(self.con, 1, i, self.display_data[line])
            i+=1
    def check_for_overlap(self):
        pass

class EquipmentDataButton(button_widget.ColoredTextButtonWidget):
    def __init__(self, parent, x, y, label="", function=None, passable=None, equip_type="", color=libtcod.light_grey):
        super().__init__(parent, x, y, label, function, passable, color)
        self.background_color = libtcod.black
        self.triggered_color = color
        self.untriggered_color = color
        self.highlight_color = color
        self.equip_type = ""

    def update(self, key, mouse):
        if self.mouse_is_in_console(mouse):
            self.background_color = libtcod.light_grey
            self.gEngine.console_set_default_background(self.con, self.background_color)
        else:
            self.background_color = libtcod.black
            self.gEngine.console_set_default_background(self.con, self.background_color)
class CompareExamine(panels.StaticPanel):
    def __init__(self, gEngine, parent, owner, x=0, y=22, w=0, h=21, title="Compare/Examine", draw_frame=True):
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
        super().__init__(gEngine, parent, x, y, w, h, title, draw_frame)
        self.owner = owner
        self.display_data = []

    def check_for_overlap(self):
        pass

    def update(self, key, mouse):
        pass
        '''if self.is_active():
            i = 1
            for line in self.display_data:
                self.gEngine.console_print(self.con, 1, i, line)
                i += 1'''

    def update_data(self, data):
        """
        Decides which data to draw based on which type of data is passed
        :param data: Object class, with an attached item component inventory item
        :return: True if data was passed, False otherwise
        """
        if data.item:
            if data.item.equipment:
                self.weapon_draw_data(data)
                return True
            if data.item.spell:
                self.consumable_draw_data(data)
                return True
            if data.item.ammo:
                pass
        else:
            self.display_data.clear()
            return False

    def weapon_draw_data(self, data):
        """

        :param data: Object class, with an attached item.equipment component inventory item
        :return:
        """
        self.display_data.clear()
        self.display_data = [
            'Name     : %s' % data.item.name,
            'Type     : %s' % data.item.equipment.type,
            'Damage   : %s' % data.item.equipment.damage,
            'Accuracy : %s' % data.item.equipment.accuracy,
            'Value    : %s' % data.item.value,
            'Effects  : '
        ]

    def consumable_draw_data(self, data):
        """

        :param data:
        :return:
        """
        self.display_data.clear()

