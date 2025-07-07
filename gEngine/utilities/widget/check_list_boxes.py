__author__ = 'GrishdaFish'
import math
import tcod as libtcod

from gEngine.utilities.widget import window_widget
class CheckBox:
    def __init__(self, gEngine, x, y, parent, label, value=False, color=libtcod.white):
        """
        A UI element that displays a checkbox in front of a text label
        :param label: the string for the check box
        :param value: the value to be modified by using this checkbox. Must be a boolean. Sets initial State
        """
        self.gEngine = gEngine
        self.original_label = label
        self.label = label
        self.display_label = ""
        self.checked_box = chr(225)
        self.unchecked_box = chr(224)
        self.is_checked = value
        self.active = parent.is_active()
        if isinstance(value, bool):
            self.value = value
        else:
            self.value = False
            raise TypeError('Variable "value" MUST be a boolean!')
        self.w = len(label) + 2
        self.h = 1
        self.x = x
        self.y = y
        self.parent = parent
        self.con = self.gEngine.console_new(self.w, self.h)
        self.base_color = color
        self.background_color = libtcod.black
        self.hovered_color = libtcod.green

    def on_exit(self):
        """
        Cleanup for this widget
        :return:
        """
        self.deactivate()
        self.gEngine.console_remove_console(self.con)

    def close(self):
        self.on_exit()

    def run(self, key, mouse):
        """
        performs all logic for this button. Do not override, override self.update instead for custom behavior
        :param key: libtcod.Key() object
        :param mouse: libtcod.Mouse() object
        :return:
        """
        if self.is_active():
            self.gEngine.console_clear(self.con)
            self.basic_mouse_input(mouse)
            self.basic_key_input(key)
            self.pre_draw_widget()
            self.update(key, mouse)
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, self.parent.con, self.x, self.y, 1.0, 1.0)

    def update(self, key, mouse):
        """
        Override this to enable custom behavior
        :param key: libtcod.Key() object
        :param mouse: libtcod.Mouse() object
        :return:
        """
        pass

    def basic_mouse_input(self, mouse):
        """
        Checks mouse info
        :param mouse:
        :return:
        """
        if self.mouse_is_in_console(mouse):
            if mouse.lbutton:
                self.toggle_check()
            self.label = self.gEngine.color_text("%s %s"%(self.get_check_box(), self.original_label), self.hovered_color)
        else:
            self.label = self.gEngine.color_text("%s %s" % (self.get_check_box(), self.original_label), self.base_color)


    def mouse_is_in_console(self, mouse):
        """
        Checks to see if the mouse is hovering over this object
        :param mouse: libtcod.Mouse() object
        :return: T/F?
        """
        if math.floor(self.x + self.parent.x) <= math.floor(mouse.cx) <= math.floor((self.parent.x + self.x) + self.w-1):
            if mouse.cy == (self.y + math.floor(self.parent.y)):
                return True
        return False

    def pre_draw_widget(self):
        """
        Sets the colors of the background and text
        :return:
        """
        if self.active:
            self.gEngine.console_set_default_background(self.con, self.background_color)
            self.gEngine.console_print(self.con, 0, 0, self.label)

    def basic_key_input(self, key):
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_active(self):
        self.active = self.parent.is_active()
        return self.active

    def toggle_activate(self):
        self.active = not self.active

    def toggle_check(self):
        self.is_checked = not self.is_checked
        self.value = not self.value

    def check(self):
        self.is_checked = True
        self.value = True

    def uncheck(self):
        self.is_checked = False
        self.value = False

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.is_checked = value
        self.vaule = value

    def get_checked(self):
        return self.is_checked

    def get_check_box(self):
        """
        Gets the proper checked box character
        :return: chr(224) for unchecked box, or chr(225) for checked box
        """
        if self.is_checked:
            return self.checked_box
        return self.unchecked_box

class RadioBox(CheckBox):
    def __init__(self, gEngine, x, y, parent, label, value, color=libtcod.white):
        super().__init__(gEngine, x, y, parent, label, value, color)
        self.checked_box = chr(self.gEngine.fonts['RADIO_CHECKED'])
        self.unchecked_box = chr(self.gEngine.fonts['RADIO_UNCHECKED'])


class CheckList(window_widget.StaticWindowWidget):
    def __init__(self, gEngine, game=None, x=0, y=0, w=0, h=5, title="", target_console=0, draw_frame=False, parent=None):
        """
        A container widget to hold multiple check boxes. use setup() to pass data, and the widget will auto generate the
        required check lists
        :param gEngine: Active instance of gEngine
        :param game: Active Game instance
        :param x: The starting X position for the widget
        :param y: The Starting Y position for the widget
        :param w: The width of the widget
        :param h: The Height of the widget
        :param title: The title to be displayed
        :param target_console: Console to blit this on top of. Defaults to root
        :param draw_frame: Boolean to toggle drawing the frame and title
        """
        super().__init__(gEngine, game, x, y, w, h, title, target_console, draw_frame)
        self.buttons = []
        self.data = []
        self.parent = parent
        # self.gEngine.console_remove_console(self.con) # this is crashing for some reason


    def setup(self, data, label):
        """
        Populates the check list with check boxes from supplied data and labels
        :param data: a list of bools for the checkboxes
        :param label: a list of strings for the label of each checkbox
        :return:
        """
        if not isinstance(data, list):
            raise TypeError("Data must be a list!")
        if not isinstance(label, list):
            raise TypeError("Label must be a list!")
        if len(label) != len(data):
            raise Exception("Label and Data must have the same number of elements!")

        i = 0
        if self.draw_frame:
            y = 1
            x = 1
        else:
            y = 0
            x = 0

        for d in data:
            if not isinstance(d, bool):
                raise TypeError("Data list must contain only bools!")
            l = label[i]

            if not isinstance(l, str):
                raise TypeError("Label list must contain only strings!")

            self.buttons.append(CheckBox(self.gEngine, x, y, self, l, d))
            if len(l) > self.width:
                self.width = len(l)
            i += 1
            y += 1
        self.height = i
        self.original_width = self.width
        self.original_height = self.height
        #if self.con:
        #    self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)

    def update(self, key, mouse):
        if self.parent:
            self.active = self.parent.is_active()
        if self.active:
            for button in self.buttons:
                button.run(key, mouse)


    def get_checkbox_data(self, label):
        """
        returns the data from the checkbox with the supplied label
        :param label: string of the requested checkbox
        :return: T/F?
        """
        for box in self.buttons:
            if box.original_label == label:
                return box.get_value()

    def activate(self):
        self.active = True

