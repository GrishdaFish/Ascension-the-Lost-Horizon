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
            " ",
            "Light Source : "
        ]
        self.use_popup = None
        self.update_data()


    def update_data(self):
        self.buttons.clear()
        key = '1h'
        equip = self.owner.fighter.gear.equipped[key]
        if equip:
            equip_button = EquipmentDataButton(self, 15, 1, equip.name.capitalize(), self.unequip_item,
                                            [self.owner.fighter.gear.equipped[key]], key, equip.color, self.owner.fighter.gear.equipped[key])
        else:
            equip_button = EquipmentDataButton(self, 15, 1, "Empty", None, None, key, libtcod.dark_grey)
        equip_button.width = self.w - 14
        self.buttons.append(equip_button)
        self.one_h_button = equip_button

        key = '2h'
        equip = self.owner.fighter.gear.equipped[key]
        if equip:
            equip_button = EquipmentDataButton(self, 15, 2, equip.name.capitalize(), self.unequip_item,
                                            [self.owner.fighter.gear.equipped[key]], key, equip.color, self.owner.fighter.gear.equipped[key])
        else:
            equip_button = EquipmentDataButton(self, 15, 2, "Empty", None, None, key, libtcod.dark_grey)
        equip_button.width = self.w - 14
        self.buttons.append(equip_button)
        self.two_h_button = equip_button

        equip = self.owner.fighter.gear.light_source
        if equip:
            torch = self.gEngine.color_text(equip.name.capitalize(), equip.color)
            torch += " (%s - %s)" % (self.gEngine.color_text("Fuel", libtcod.brass), self.gEngine.color_text(equip.item.equipment.fuel, get_fuel_color(equip)))
            clean_label = "%s (Fuel - %s)" % (equip.name, equip.item.equipment.fuel)
            equip_button = EquipmentDataButton(self, 15, 6, torch, self.unequip_item,
                                            [equip], key, equip.color, equip, clean_label=clean_label)
        else:
            equip_button = EquipmentDataButton(self, 15, 6, "Empty", None, None, key, libtcod.dark_grey)
        equip_button.width = self.w - 14
        self.buttons.append(equip_button)
        self.torch_button = equip_button

    def unequip_item(self, item):
        print("Unequipping Item")
        self.popup(item)

    def update(self, key, mouse):
        self.draw_static_data()
        for button in self.buttons:
            button.run(key, mouse)

    def draw_static_data(self):
        i = 1
        for line in self.display_data:
            self.gEngine.console_print(self.con, 1, i, line)
            i += 1
        item = self.owner.fighter.gear.gimmie_da_weapon()
        item2 = self.owner.fighter.gear.gimmie_da_weapon(off_hand=True)
        damage_total = [0, 0, 0, 0]
        if item is not None and self.owner.fighter.gear.is_weapon(item):
            damage_total[0] += item.item.equipment.damage[0]
            damage_total[1] += item.item.equipment.damage[1]
            damage_total[3] += item.item.equipment.damage[3]
        if item2 is not None and self.owner.fighter.gear.is_weapon(item2):
            damage_total[0] += item2.item.equipment.damage[0]
            damage_total[1] += item2.item.equipment.damage[1]
            damage_total[3] += item2.item.equipment.damage[3]
        if item or item2:
            damage = '%dd%d+%d' % (
                damage_total[0], damage_total[1], damage_total[3])
            text = 'Damage       :%s' % self.gEngine.color_text(damage, libtcod.green)
            self.gEngine.console_print(self.con, 1, 3, text)
            accuracy = self.owner.fighter.stat.get_stat("Accuracy")
            # accuracy += game.player.fighter.get_skill(item.item.equipment.damage_type).get_bonus()
            text = 'Accuracy     :%s' % self.gEngine.color_text(str(accuracy), libtcod.green)
            self.gEngine.console_print(self.con, 1, 4, text)
    def popup(self, item):
        """
        Creates and displays a confirmation popup
        :param item: The item to be used/Equipped
        :return:
        """
        if is_equipment(item):
            message = "Do you want to un-equip %s" % item.name.capitalize()
            title = "Un-Equip item?"
        else:
            return

        i = ItemUnequipConfirmPopup(self.gEngine,x=self.w, y=self.h/2,title=title, owner=self.owner, parent=self, message=message)
        i.update_data(item)
        i.x = self.w - i.width/2
        i.activate()
        self.gEngine.add_module(i)
        self.use_popup = i

    def close_use_popup(self):
        """
        Helper Cleanup Function for the confirm popup
        :return:
        """
        self.use_popup.close()