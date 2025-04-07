__author__ = 'GrishdaFish'
import math
from gEngine.utilities.user_interface import menu
import tcod as libtcod


class ButtonWidget:
    def __init__(self, parent, x, y, label, function, passable=None):
        """
        A button widget with a function pointer attached to a widget window
        Pass a function pointer to make it do stuff
        If the function requires anything to be passed to the function, pass a list of required data
        to "passable"
        Be sure to run on_exit() during your widget window's exit function to remove this button's console to prevent
        memory leaks.

        Can act as it's own module.  - Untested, use at own risk

        :param parent: The window widget this button is attached to
        :param x: The position relative to the Parent
        :param y: Position relative to the Parent
        :param label: What this button says
        :param function: Function pointer that triggers when clicked
        :param passable: Any values that need to be passed to the function pointer. List.
        """
        self.parent = parent
        self.gEngine = parent.gEngine
        self.x = x
        self.y = y
        self.label = " " + label + " "
        self.function = function
        self.width = len(self.label)
        self.height = 1
        self.con = self.gEngine.console_new(self.width, self.height)
        self.active = True
        self.passable = passable
        self.original_label = self.label
        self.triggered = False
        self.untriggered_color = libtcod.dark_grey
        self.triggered_color = libtcod.white

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.deactivate()
        self.gEngine.console_remove_console(self.con)

    def close(self):
        self.on_exit()

    def update(self, key, mouse):
        """
        over-ride to enable custom behavior
        :param key:
        :param mouse:
        :return:
        """
        pass

    def trigger(self):
        """
        Do not over-ride unless you know what you're doing
        :return: Returns what ever the function pointer will return
        """
        if self.function:
            if self.passable:
                return self.function(*self.passable)  # works similar to *args, only in reverse
            return self.function()

    def mouse_is_in_console(self, mouse):
        if math.floor(self.x + self.parent.x) <= math.floor(mouse.cx) <= math.floor(((self.parent.x + self.x)) + self.width):
            if mouse.cy == (self.y + math.floor(self.parent.y)):
                return True
        return False

    def run(self, key, mouse):
        """
        Call this function in your widget
        :param key:
        :param mouse:
        :return: returns the trigger() return value
        """
        if not self.parent.collapsed and not self.parent.minimized:
            self.parent.gEngine.console_clear(self.con)
            returnable = self.basic_mouse_input(mouse)
            if not self.active:  # we return early in case trigger acts like a close function
                return
            self.pre_draw_widget()
            self.update(key, mouse)
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, self.parent.con, self.x, self.y, 1.0, 1.0)
            return returnable

    def basic_mouse_input(self, mouse):
        if self.mouse_is_in_console(mouse):
            self.label = menu.color_text(self.original_label, libtcod.dark_orange)
            if mouse.lbutton:
                return self.trigger()
        else:
            if not self.triggered:
                self.label = menu.color_text(self.original_label, self.untriggered_color)
            else:
                self.label = menu.color_text(self.original_label, self.triggered_color)

    def pre_draw_widget(self):
        if self.active:
            r, g, b = libtcod.lighter_grey
            self.gEngine.console_set_default_background(self.con, r, g, b)
            self.gEngine.console_print(self.con, 0, 0, self.label)


class TextButtonWidget(ButtonWidget):
    def __init__(self, parent, x, y, label, function, passable=None):
        super().__init__(parent, x, y, label, function, passable)
        self.label = label
        self.original_label = label
        self.width = len(self.label)
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)

    def pre_draw_widget(self):
        if self.active:
            self.gEngine.console_print(self.con, 0, 0, self.label)