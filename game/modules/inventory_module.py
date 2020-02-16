from gEngine import custom_font
from gEngine.utilities.widget import button_widget, window_widget


class ContextMenu:
    def close(self):
        pass
    def update(self):
        pass
    def setup(self):
        pass

class InventoryModule(window_widget.WindowWidget):
    def close(self):
        for all_the_shit in self.widgets:
            all_the_shit.close()
        self.gEngine.remove_module(self)
        self.deactivate()

    def update(self, key, mouse):
        self.refresh_widgets()
        for all_the_shit in self.widgets:
            if all_the_shit.run(key, mouse):
                self.widgets.remove(all_the_shit)

    def refresh_widgets(self):
        self.title = "Gold: " + str(self.game.player.fighter.money)
        self.original_title = "Gold: " + str(self.game.player.fighter.money)
        self.items = self.game.player.fighter.inventory
        self.index = 1
        self.widgets = []

        if self.items:
            for item in self.items:
                if item.item.stackable:
                    name = item.char + " " + item.name + " (" + str(item.item.qty) + ")"
                else:
                    name = item.char + " " + item.name
                self.widgets.append(button_widget.TextButtonWidget(self, 1, self.index, name, item.item.use,
                                                                   [self.game.player.fighter.inventory,
                                                                    self.game.player, self.game]))
                self.index += 1
        else:
            self.gEngine.console_print(self.con, 1, 1, "Inventory is empty")

class EquipmentModule(InventoryModule):
    def refresh_widgets(self):
        self.slots = self.game.player.fighter.gear.gimmie_da_slots_all()
        self.gear = self.game.player.fighter.gear.gimmie_da_quips()
        self.index = 2
        self.widgets = []

        main_hand = self.game.player.fighter.gear.gimmie_da_weapon()
        if main_hand:
            main_hand_icon = main_hand.char
        else:
            main_hand_icon = chr(custom_font.glove)
        off_hand = self.game.player.fighter.gear.gimmie_da_weapon(off_hand=True)
        if off_hand:
            off_hand_icon = off_hand.char
        else:
            if main_hand and main_hand.item.equipment.handed == 2:
                off_hand_icon = main_hand.char
            else:
                off_hand_icon = chr(custom_font.glove)

        # paper doll layout
        # self.gEngine.console_print(self.con, 5, 2, chr(custom_font.shoulder))
        # self.gEngine.console_print(self.con, 6, 2, chr(custom_font.helm))
        # self.gEngine.console_print(self.con, 7, 2, chr(custom_font.neck))
        # self.gEngine.console_print(self.con, 5, 3, chr(custom_font.cloak))
        # self.gEngine.console_print(self.con, 6, 3, chr(custom_font.torso))
        # self.gEngine.console_print(self.con, 7, 3, chr(custom_font.arms))
        # self.gEngine.console_print(self.con, 4, 4, main_hand_icon)
        # self.gEngine.console_print(self.con, 5, 4, chr(custom_font.ring))
        # self.gEngine.console_print(self.con, 6, 4, chr(custom_font.legs))
        # self.gEngine.console_print(self.con, 7, 4, chr(custom_font.glove))
        # self.gEngine.console_print(self.con, 8, 4, off_hand_icon)
        # self.gEngine.console_print(self.con, 6, 5, chr(custom_font.boot))

        self.gEngine.console_print(self.con, 2, 5, chr(custom_font.shoulder))
        self.gEngine.console_print(self.con, 2, 4, chr(custom_font.helm))
        self.gEngine.console_print(self.con, 2, 12, chr(custom_font.neck))
        self.gEngine.console_print(self.con, 2, 11, chr(custom_font.cloak))
        self.gEngine.console_print(self.con, 2, 8, chr(custom_font.torso))
        self.gEngine.console_print(self.con, 2, 6, chr(custom_font.arms))
        self.gEngine.console_print(self.con, 2, 2, main_hand_icon)
        self.gEngine.console_print(self.con, 2, 13, chr(custom_font.ring))
        self.gEngine.console_print(self.con, 2, 9, chr(custom_font.legs))
        self.gEngine.console_print(self.con, 2, 7, chr(custom_font.glove))
        self.gEngine.console_print(self.con, 2, 3, off_hand_icon)
        self.gEngine.console_print(self.con, 2, 10, chr(custom_font.boot))

        if self.gear:
            for gear in self.gear:
                if gear:
                    self.widgets.append(button_widget.TextButtonWidget(self, 4, self.index, gear.name, gear.item.use,
                                                                   [self.game.player.fighter.inventory,
                                                                    self.game.player, self.game]))
                else:
                    self.gEngine.console_print(self.con, 4, self.index, "Empty")
                self.index += 1
        else:
            self.gEngine.console_print(self.con, 1, 1, "Get Some Equipment!")
