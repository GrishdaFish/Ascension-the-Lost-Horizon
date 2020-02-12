__author__ = 'GrishdaFish'
from gEngine.utilities.widget import window_widget, button_widget
import tcod as libtcod

class Alert(window_widget.WindowWidget):
    """ Basic alert widget, returns no values """
    def close(self):
        self.gEngine.remove_module(self)
        self.ok_button.close()

    def setup(self, message):
        self.message = message
        self.width = len(message) + 2
        self.original_width = self.width
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)
        self.title_x_position = self.width / 2 - (len(self.title) / 2)
        self.ok_button = button_widget.ButtonWidget(self, self.width/2 - 2, 3, "Ok", self.close)

    def update(self, key, mouse):
        if self.active:
            # notify user of something like bad password, no user name/pass, etc.. Just a confirm widget
            if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_ESCAPE or key.vk == libtcod.KEY_SPACE:
                self.close()
            self.gEngine.console_print(self.con, 1, 1, self.message)
            self.ok_button.run(key, mouse)

class Confirm(window_widget.WindowWidget):
    """ Confirm modal asking for a yes or no, we should add line wrapping too """
    def close(self):
        self.gEngine.remove_module(self)
        self.ok_button.close()
        self.cancel_button.close()

    def setup(self, message, callback, ok="Ok", cancel="Cancel"):
        """ Wherever you create the popup you will need a callback function that grabs and returns your response
            :param: callback is the function that grabs the response
            :param: ok and cancel change the button text """
        self.message = message
        self.width = len(message) + 2
        self.original_width = self.width
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)
        self.title_x_position = self.width / 2 - (len(self.title) / 2)
        self.callback = callback
        self.ok_button = button_widget.ButtonWidget(self, len(ok) + 3, 4, ok, self.callback, [True])
        self.cancel_button = button_widget.ButtonWidget(self, self.width - len(cancel) - 3, 4, cancel, self.callback, [False])

    def update(self, key, mouse):
        if self.active:
            self.gEngine.console_print(self.con, 2, 2, self.message)
            self.ok_button.run(key, mouse)
            self.cancel_button.run(key, mouse)

class MultiConfirm(window_widget.WindowWidget):
    """ Confirm modal asking for a multiple choice selection """
    def close(self):
        self.deactivate()
        self.gEngine.remove.module(self)
        for button in self.buttons:
            button.close()

    def setup(self, message, callbacks=[], passables=[], button_text=[]):
        if len(callbacks) > 0 and len(callbacks) == len(passables) == len(button_text):
            self.message = message
            self.original_width = self.width
            if len(callbacks) > 3:
                self.height = self.height + (len(callbacks) / 3)  # starting with 3 buttons per line, we can see if this feels ok
            button_lengths = []
            button_total_lengths = 0
            for text in button_text:
                button_lengths.append(len(text))
                button_total_lengths += len(text)
            button_lengths.sort(reverse=True)
            worst_case = button_lengths[0] * 3
            if len(self.message) > worst_case:
                self.width = len(message) + 2
            else:
                self.width = worst_case + 4

            self.gEngine.console_remove_console(self.con)
            self.con = self.gEngine.console_new(self.width, self.height)
            self.title_x_position = self.width / 2 - (len(self.title) / 2)

            button_x_positions = [int(self.width / 5), int(self.width / 2), int(self.width - (self.width / 5))]
            starting_y = 4
            iterations = 0
            self.buttons = []
            for btn_x, cb, arg, btn in zip(button_x_positions, callbacks, passables,  button_text):
                self.buttons.append(button_widget.ButtonWidget(self, btn_x, starting_y + int(iterations / 3), btn, cb, arg))
                iterations += 1


    def update(self, key, mouse):
        if self.active:
            self.gEngine.console_print(self.con, 2, 2, self.message)
            for button in self.buttons:
                button.run(key, mouse)