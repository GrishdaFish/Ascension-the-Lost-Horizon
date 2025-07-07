__author__ = 'GrishdaFish'
from game.user_interface.widgets.inventory_support_widgets import *

class EquipmentDataButton(button_widget.ColoredTextButtonWidget):
    def __init__(self, parent, x, y, label="", function=None, passable=None, equip_type="", color=libtcod.light_grey, data=None):
        super().__init__(parent, x, y, label, function, passable, color)
        self.background_color = libtcod.black
        self.triggered_color = color
        self.untriggered_color = color
        self.highlight_color = color
        self.equip_type = ""
        self.data = data

    def update(self, key, mouse):
        if self.mouse_is_in_console(mouse):
            self.background_color = libtcod.lightest_grey
            self.gEngine.console_set_default_background(self.con, self.background_color)
            self.parent.parent.compare_widget.update_data(self.data)
        else:
            self.background_color = libtcod.black
            self.gEngine.console_set_default_background(self.con, self.background_color)


class InventoryCheckBox(check_list_boxes.CheckBox):
    def __init__(self, gEngine, x, y, parent, label="", value=False, color=libtcod.white, data=None):
        super().__init__(gEngine, x, y, parent, label, value=False, color=libtcod.white)
        self.data = data

class CheckAllCheckBox(check_list_boxes.CheckBox):
    def update(self, key, mouse):
        if self.mouse_is_in_console(mouse):
            if mouse.lbutton:
                for box in self.parent.check_boxes:
                    box.set_value(self.get_value())