__author__ = 'GrishdaFish'
from gEngine.utilities.user_interface import menu
import math
import tcod as libtcod

class TextInputWidget:
    def __init__(self, parent, label,  x, y, width):
        """
        A text gathering widget for the window widget system.
        Nothing too fancy
        Click anywhere in this widget to start typing. Click anywhere outside of this widget to stop
        Enter to submit data

        Be sure to run on_exit() during your widget window's exit function to remove this button's console to prevent
        memory leaks.

        Can act as it's own module.  - Untested, use at own risk

        :param parent: The window widget this is attached to
        :param label: The text before the input
        :param x: Position relative to parent
        :param y: Position relative to parent
        :param width: the width of the entire widget
        """
        self.width = width
        self.x = x
        self.y = y
        self.max_char = self.width - (len(label) + 1)
        if self.width < len(label) + 1:
            self.width = len(label) + 1
        self.parent = parent
        self.gEngine = parent.gEngine
        self.label = label
        self.original_label = label
        self.target = parent.con
        self.con = self.gEngine.console_new(self.width, 1)
        self.active = True
        self.in_text = False
        self.is_blinking = False
        self.carrot = "|"
        self.text_field = ""
        self.frame_blink = 0
        self.enabled = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def close(self):
        self.on_exit()

    def on_exit(self):
        self.deactivate()
        self.gEngine.console_remove_console(self.con)

    def force_activate(self):
        """
        Use this to force text to be gathered without clicking inside of this widget
        :return:
        """
        self.in_text = True

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def toggle_carrot(self):
        if self.is_blinking:
            self.carrot = ' '
        else:
            self.carrot = "|"
        self.is_blinking = not self.is_blinking

    def mouse_is_in_console(self, mouse):
        if (self.x + self.parent.x) <= mouse.cx <= (self.parent.x + self.x) + self.width:
            if mouse.cy == (self.y + math.floor(self.parent.y)):
                return True
        return False

    def update(self, key, mouse):
        """
        Over-ride For custom behavior
        :param key:
        :param mouse:
        :return:
        """
        pass

    def get_text(self):
        """
        Grab the text field regardless of enter being pressed
        :return:
        """
        return self.text_field

    def run(self, key, mouse):
        """
        Call this function in your widget to use this widget
        :param key:
        :param mouse:
        :return: self.text_field if Enter was pressed, otherwise None
        """
        self.gEngine.console_clear(self.con)
        input = self.handle_input(key, mouse)
        self.update(key, mouse)
        self.prepare_render()
        self.run_blink()
        if self.active:
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, self.target, self.x, self.y, 1.0, 1.0)
        if input:
            return self.text_field
        return None

    def run_blink(self):
        if self.in_text:
            x_pos = len(self.original_label) + len(self.text_field)
            self.gEngine.console_print(self.con, x_pos, 0, self.carrot)
        if self.frame_blink < 9:
            self.frame_blink += 1
        else:
            self.frame_blink = 0
            self.toggle_carrot()

    def handle_input(self, key, mouse):
        if self.mouse_is_in_console(mouse):
            self.label = menu.color_text(self.original_label, libtcod.green)
            if mouse.lbutton:
                self.in_text = True
        else:
            self.label = menu.color_text(self.original_label, libtcod.white)
            if mouse.lbutton:
                self.in_text = False
        if key.c:
            if len(self.text_field) > self.max_char:
                pass
            elif self.in_text:
                self.text_field += chr(key.c)
        if key.vk == libtcod.KEY_BACKSPACE:
            if self.in_text:
                if len(self.text_field) > 0:
                    self.text_field = self.text_field[:-1]
        if key.vk == libtcod.KEY_ENTER:
            if self.in_text:
                self.in_text = False
                return True
        return False

    def prepare_render(self):
        if self.active:
            text = self.label + self.text_field
            self.gEngine.console_print(self.con, 0, 0, text)
