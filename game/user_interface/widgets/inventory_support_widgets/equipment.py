__author__ = 'GrishdaFish'

from game.user_interface.widgets.inventory_support_widgets import *

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
        self.update_data()


    def unequip_item(self, item):
        print("Unequipping Item")

    def setup(self, data):
        self.equipment_slots = self.owner.fighter.gimmie_da_slots()

    def update(self, key, mouse):
        self.draw_static_data()
        for button in self.buttons:
            button.run(key, mouse)

    def update_data(self):
        self.buttons.clear()
        i = 1
        for item in self.owner.fighter.gear.equipped:
            if not item == "1h" and not item == "2h":
                if self.owner.fighter.gear.equipped[item]:
                    equip = self.owner.fighter.gear.equipped[item]
                    b = EquipmentDataButton(self, 13, i, equip.name.capitalize(), self.unequip_item,
                                            [self.owner.fighter.gear.equipped[item]], item, equip.color,
                                            self.owner.fighter.gear.equipped[item])
                    b.width = self.w - 14
                    self.buttons.append(b)
                else:
                    equip = "Empty"
                    b = EquipmentDataButton(self, 13, i, equip, None, None, item, libtcod.dark_grey)
                    b.width = self.w - 14
                    self.buttons.append(b)
                i += 1
    def update_widget_data(self, data):
        self.data = data

    def draw_static_data(self):
        i=1
        for line in self.display_data:
            self.gEngine.console_print(self.con, 1, i, self.display_data[line])
            i+=1
