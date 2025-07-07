__author__ = 'GrishdaFish'

from game.user_interface.widgets.inventory_support_widgets import *

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

    def update(self, key, mouse):
        if self.parent.is_active():
            i = 1
            for line in self.display_data:
                self.gEngine.console_print(self.con, 1, i, line)
                i += 1

    def update_data(self, data):
        """
        Decides which data to draw based on which type of data is passed
        :param data: Object class, with an attached item component inventory item
        :return: True if data was passed, False otherwise
        """
        if data:
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
        else:
            return False

    def weapon_draw_data(self, data=None):
        """

        :param data: Object class, with an attached item.equipment component inventory item
        :return:
        """
        if data:
            self.display_data.clear()
            self.display_data = [
                'Name     : %s' % data.name.capitalize(),
                'Type     : %s' % data.item.equipment.type.capitalize()
            ]

            if is_weapon(data, self.owner):
                self.display_data.append('Damage   : %s' % data.item.equipment.damage)
                self.display_data.append('Accuracy : %s' % data.item.equipment.accuracy)

            elif is_armor(data, self.owner):
                self.display_data.append('Armor    : %s' % data.item.equipment.bonus)
                self.display_data.append('Penalty  : %s' % data.item.equipment.penalty)
                self.display_data.append('Location : %s' % data.item.equipment.location.capitalize())

            elif is_light(data, self.owner):
                self.display_data.append('Fuel     : %s' % data.item.equipment.fuel)
                self.display_data.append('Max Fuel : %s' % data.item.equipment.max_fuel)

            self.display_data.append('Value    : %s' % data.item.value)

            if not is_light(data, self.owner):
                self.display_data.append('Effects  : ')


    def consumable_draw_data(self, data=None):
        """

        :param data:
        :return:
        """
        self.display_data.clear()

