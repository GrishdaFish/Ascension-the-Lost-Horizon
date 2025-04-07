__author__ = 'GrishdaFish'
import math
from gEngine.utilities.user_interface import menu
from gEngine.utilities.widget import button_widget
import tcod as libtcod


class ButtonGroupWidget:
    def __init__(self, parent, x, y, width, height=1, border=False, max_active=10):
        self.parent = parent
        self.gEngine = parent.gEngine
        self.x = x
        self.y = y
        self.border = border
        self.active = True
        if border:
            width += 2
            height += 2
        self.width = width
        self.height = height
        self.con = self.gEngine.console_new(self.width, self.height)
        self.buttons = []
        self.button_id = 0

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = True

    def disable_all(self):
        for button in self.buttons:
            button.disable()

    def on_exit(self):
        self.deactivate()
        for button in self.buttons:
            button.close()
        self.buttons = []
        self.gEngine.console_remove_console(self.con)

    def get_active_id(self):
        """
        Returns the currently enabled button, or None if all are disabled
        :return:
        """
        for button in self.buttons:
            if button.enabled:
                return button.id
        return None

    def add_button(self, button):
        try:
            if isinstance(button, GroupButton):
                button.id = self.button_id
                self.button_id += 1
                self.buttons.append(button)
                length = 0
                for button in self.buttons:
                    length += len(button.label) + 1
                if length > self.width:
                    self.width = length
                    self.gEngine.console_remove_console(self.con)
                    self.con = self.gEngine.console_new(self.width, self.height)
            else:
                raise Exception("Must use Group Button!")
        except Exception as ex:
            self.gEngine.log_message(ex, "Error")

    def run(self, key, mouse):
        self.gEngine.console_clear(self.con)
        self.pre_draw_widget()
        self.update(key, mouse)
        for button in self.buttons:
            returnable, id = button.run(key, mouse)
            if id is not None:
                for b in self.buttons:
                    if b.id != id:
                        b.disable()
        self.gEngine.console_blit(self.con, 0, 0, 0, 0, self.parent.con, self.x, self.y, 1.0, 1.0)

    def update(self, key, mouse):
        pass

    def mouse_is_in_console(self, mouse):
        if self.x <= mouse.cx <= self.x + math.floor(self.width):
            if self.y <= mouse.cy <= self.y + math.floor(self.height):
                return True
        return False

    def pre_draw_widget(self):
        start_position = 0
        if self.border:
            self.gEngine.console_print_frame(self.con, 0, 0, self.width, self.height, True)
            start_position += 1
        for button in self.buttons:
            button.x = start_position
            if self.border:
                button.y = 1
            start_position = button.x + len(button.original_label) + 1


class GroupButton(button_widget.ButtonWidget):
    def __init__(self, parent, x, y, label, function=None, passable=None):
        super().__init__(parent, x, y, label, function, passable)
        self.enabled = False
        self.id = None

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def trigger(self):
        """
        Do not over-ride this unless you REALLY know what you're doing.
        Pass your function pointer and relevant data instead
        :return:
        """
        if not self.enabled:
            self.enable()
            if self.function:
                if self.passable:
                    return self.function(*self.passable), True  # works similar to *args, only in reverse
                return self.function(), True
            else:
                return None, True
        else:
            self.disable()
        return None, None

    def pre_draw_widget(self):
        if self.active:
            if self.enabled:
                r, g, b = libtcod.lighter_grey
            else:
                r, g, b = libtcod.darker_grey
            self.gEngine.console_set_default_background(self.con, r, g, b)
            self.gEngine.console_print(self.con, 0, 0, self.label)

    def run(self,  key, mouse):
        self.gEngine.console_clear(self.con)
        returnable, pressed = self.basic_mouse_input(mouse)
        if not self.active:  # we return early in case trigger acts like a close function
            return None, None
        self.pre_draw_widget()
        self.update(key, mouse)
        self.gEngine.console_blit(self.con, 0, 0, 0, 0, self.parent.con, self.x, self.y, 1.0, 1.0)
        if pressed:
            return returnable, self.id
        return returnable, None

    def mouse_is_in_console(self, mouse):
        if math.floor(self.x + self.parent.x + self.parent.parent.x) <= math.floor(mouse.cx) \
                <= math.floor(((self.parent.x + self.parent.parent.x+ self.x)) + self.width):
            if mouse.cy == (self.y + math.floor(self.parent.y+self.parent.parent.y)):
                return True
        return False

    def basic_mouse_input(self, mouse):
        if self.mouse_is_in_console(mouse):
            self.label = menu.color_text(self.original_label, libtcod.dark_orange)
            if mouse.lbutton:
                r1, r2 = self.trigger()
                return r1, r2
        else:
            self.label = menu.color_text(self.original_label, libtcod.dark_grey)
        return None, None