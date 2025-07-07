__author__ = 'GrishdaFish'

from game.user_interface.widgets.inventory_support_widgets import *

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
        self.buttons = []
        self.one_h_button = None
        self.two_h_button = None
        self.torch_button = None
        self.display_data = [
            "Main Hand    : ",
            "Off Hand     : ",
            " ",
            " ",
            "Light Source : "
        ]
        self.update_data()


    def update_data(self):
        self.buttons.clear()
        key = '1h'
        equip = self.owner.fighter.gear.equipped[key]
        if equip:
            equip_button = EquipmentDataButton(self, 15, 2, equip.name.capitalize(), self.unequip_item,
                                            [self.owner.fighter.gear.equipped[key]], key, equip.color, self.owner.fighter.gear.equipped[key])
        else:
            equip_button = EquipmentDataButton(self, 15, 2, "Empty", None, None, key, libtcod.dark_grey)
        equip_button.width = self.w - 14
        self.buttons.append(equip_button)
        self.one_h_button = equip_button

        key = '2h'
        equip = self.owner.fighter.gear.equipped[key]
        if equip:
            equip_button = EquipmentDataButton(self, 15, 3, equip.name.capitalize(), self.unequip_item,
                                            [self.owner.fighter.gear.equipped[key]], key, equip.color, self.owner.fighter.gear.equipped[key])
        else:
            equip_button = EquipmentDataButton(self, 15, 3, "Empty", None, None, key, libtcod.dark_grey)
        equip_button.width = self.w - 14
        self.buttons.append(equip_button)
        self.two_h_button = equip_button

        equip = self.owner.fighter.gear.light_source
        if equip:
            equip_button = EquipmentDataButton(self, 15, 6, equip.name.capitalize(), self.unequip_item,
                                            [equip], key, equip.color, equip)
        else:
            equip_button = EquipmentDataButton(self, 15, 6, "Empty", None, None, key, libtcod.dark_grey)
        equip_button.width = self.w - 14
        self.buttons.append(equip_button)
        self.torch_button = equip_button

    def unequip_item(self, item):
        print("Unequipping Item")

    def update(self, key, mouse):
        self.draw_static_data()
        for button in self.buttons:
            button.run(key, mouse)

    def draw_static_data(self):
        i = 2
        for line in self.display_data:
            self.gEngine.console_print(self.con, 1, i, line)
            i += 1
