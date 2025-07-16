__author__ = 'GrishdaFish'

from game.user_interface.widgets.inventory_support_widgets import *

class ItemUseConfirmPopup(popups.Confirm):
    def __init__(self, gEngine, game=None, x=0, y=0, w=0, h=5, title="", target_console=0, draw_frame=True, owner=None, parent=None, message=""):
        super().__init__(gEngine, game, x, y, w, h, title, target_console, draw_frame)
        self.data = None
        self.parent = parent
        self.owner = owner
        self.message = message
        self.setup(self.message, None)

    def extra_update(self, key, mouse):
        self.gEngine.bring_module_to_front(self)

    def setup(self, message = "", callback=None, ok="Ok", cancel="Cancel"):
        self.message = message
        self.width = len(message) + 4
        self.original_width = self.width
        #self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)
        self.title_x_position = self.width / 2 - (len(self.title) / 2)
        #self.callback = callback
        self.ok_button = button_widget.ButtonWidget(self, len(ok) + 3, 4, ok, self.trigger, [True])
        self.cancel_button = button_widget.ButtonWidget(self, self.width - len(cancel) - 5, 4, cancel, self.trigger,[False])

    def update_data(self, data):
        self.data = data

    def trigger(self, value):
        if self.parent.parent.is_active() and self.owner:
            if not value:
                print("Cancel")
                self.parent.close_use_popup()
            else:
                if not is_equipment(self.data):
                    # Use item
                    print("Use Item")
                    self.parent.use_item(self.data)
                    self.parent.close_use_popup()
                else:
                    self.owner.fighter.gear.quip_it(self.data)
                    # self.owner.fighter.inventory.remove(self.data)
                    self.parent.close_use_popup()
                self.parent.parent.update_data()

class ItemUnequipConfirmPopup(ItemUseConfirmPopup):
    def trigger(self, value):
        if self.parent.parent.is_active() and self.owner:
            if not value:
                print("Cancel")
                self.parent.close_use_popup()
            else:
                if is_equipment(self.data):
                    self.owner.fighter.gear.unquip_it(self.data)
                    self.parent.close_use_popup()
                self.parent.parent.update_data()