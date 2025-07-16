__author__ = 'GrishdaFish'

from game.user_interface.widgets.inventory_support_widgets import *

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
        self.check_boxes = []

        self.exit_button = button_widget.ButtonWidget(self, self.w - 8, self.h - 1, 'Exit', self.parent.close)
        self.drop_button = button_widget.ButtonWidget(self, 2, self.h - 1, 'Drop', self.drop_items)
        self.buttons.append(self.exit_button)
        self.buttons.append(self.drop_button)

        self.check_all = CheckAllCheckBox(self.gEngine, 1, self.h-4, self, "Check/Uncheck All")
        #self.check_boxes.append(self.check_all)

        self.update_data()
        self.use_popup = None
        self.used_item = None

    def setup(self, *args, **kwargs):
        pass

    def update_data(self):
        """
        Creates new buttons for the inventory screen. Called after every time the inventory updates
        :return:
        """
        self.buttons = []
        self.check_boxes = []

        self.buttons.append(self.exit_button)
        self.buttons.append(self.drop_button)

        #self.check_boxes.append(self.check_all)

        i = 1
        for item in self.owner.fighter.inventory:
            itm = self.gEngine.color_text(item.name.capitalize(), item.color)
            clean_label = item.name
            if item.item.stackable:
                itm += " (%s)" % self.gEngine.color_text(str(item.item.qty), libtcod.green)
                clean_label += " (%s)" % str(item.item.qty)
            elif is_light(item, self.owner):
                itm += " (%s - %s)" % (self.gEngine.color_text("Fuel", libtcod.brass), self.gEngine.color_text(str(item.item.equipment.fuel), get_fuel_color(item)))
                clean_label += " (Fuel - %s)" % str(item.item.equipment.fuel)
            item_button = EquipmentDataButton(self, 3, i, itm, self.popup, [item], "", item.color, item, clean_label=clean_label)
            item_button.width = self.w - 2
            self.buttons.append(item_button)

            check_box = InventoryCheckBox(self.gEngine, 1, i, self, data=item)
            self.check_boxes.append(check_box)
            i += 1

    def use_item(self, item):
        """
        Uses a consumable item.
        :param item:
        :return:
        """
        self.parent.game.use_item(item)
        self.parent.close()

    def drop_items(self):
        """
        Drops items that are selected by a checkbox to drop
        :return:
        """
        items_to_drop = []
        for box in self.check_boxes:
            if box.get_checked():
                item = box.data
                if item:
                    items_to_drop.append(item)
        for item in items_to_drop:
            item.objects = self.parent.game.objects
            item.item.drop(self.owner.fighter.inventory, self.owner, False)
            item.send_to_back()
        self.parent.update_data()

    def popup(self, item):
        """
        Creates and displays a confirmation popup
        :param item: The item to be used/Equipped
        :return:
        """
        if is_equipment(item):
            message = "Do you want to equip %s" % item.name.capitalize()
            title = "Equip item?"
        else:
            message = "Do you want to use %s" % item.name.capitalize()
            title = "Use Item"
        self.build_popup(message, title, item)

    def close_use_popup(self):
        """
        Helper Cleanup Function for the confirm popup
        :return:
        """
        self.use_popup.close()

    def update(self, key, mouse):
        """
        Main update function for this widget. gets called in the inhereted class's run(key, mouse) function
        :param key: libtcod.Key object
        :param mouse: libtcod.Mouse object
        :return:
        """
        if self.parent.is_active():
            gold = self.gEngine.color_text(self.owner.fighter.money, libtcod.gold)
            self.gEngine.console_print(self.con, 1, self.h-3, "Gold: %s" % gold)
            self.check_all.run(key, mouse)
            for box in self.check_boxes:
                box.run(key, mouse)
            for button in self.buttons:
                if self.parent.is_active():
                    button.run(key, mouse)

    def build_popup(self, message, title, item):
        i = ItemUseConfirmPopup(self.gEngine,x=self.w, y=self.h/2,title=title, owner=self.owner, parent=self, message=message)
        i.update_data(item)
        i.x = self.w - i.width/2
        i.activate()
        self.gEngine.add_module(i)
        self.use_popup = i