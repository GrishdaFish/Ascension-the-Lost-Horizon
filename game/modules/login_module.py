__author__ = 'GrishdaFish'

import math
from gEngine.utilities.widget import window_widget, button_widget, text_input_widget
from gEngine.utilities.user_interface import menu

import tcod as libtcod

class LoginPopup(window_widget.WindowWidget):
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


class LoginMenu(window_widget.WindowWidget):
    def close(self):
        self.gEngine.remove_module(self)
        self.deactivate()
        self.user_widget.close()
        self.pass_widget.close()
        self.submit_button.close()

    def setup(self):
        self.user_text = "Username:"
        self.pass_text = "Password:"
        self.user_name = None
        self.password = None
        self.user_input = False
        self.pass_input = False

        self.user_widget = text_input_widget.TextInputWidget(self, self.user_text, 1, 1, self.width - 2)
        self.user_widget.force_activate()
        self.pass_widget = text_input_widget.TextInputWidget(self, self.pass_text, 1, 2, self.width - 2)
        self.submit_button = button_widget.ButtonWidget(self, self.width/2 - 3, 4, "Submit", self.validate)


    def update(self, key, mouse):
        if not self.collapsed and not self.minimized:
            # new text widget. Returns text field if Enter key was pressed, otherwise None
            user_input = self.user_widget.run(key, mouse)
            if user_input:
                print(user_input)
                self.pass_widget.force_activate()
                self.user_input = True
                return
            # new text widget, returns text field if enter was pressed, Otherwise None
            pass_input = self.pass_widget.run(key, mouse)
            if pass_input:
                self.pass_input = True
                return

            if self.user_input and self.pass_input:
                self.validate()

            # button widget, clicking it activates function pointer, returns what ever the function pointer returns
            self.submit_button.run(key, mouse)

    def validate(self):
        self.user_name = self.user_widget.get_text()
        self.password = self.pass_widget.get_text()

        if len(self.user_name) > 24:
            data = "Username cannot be more than 25 characters long"
            pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2), self.gEngine.SCREEN_HEIGHT / 2 - 3, 1,
                             5, "Alert")
            pop.setup(data)
            self.gEngine.add_module(pop)

        elif len(self.password) > 24:
            data = "Password cannot be more than 25 characters long"
            pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2), self.gEngine.SCREEN_HEIGHT / 2 - 3, 1,
                             5, "Alert")
            pop.setup(data)
            self.gEngine.add_module(pop)

        if len(self.user_name) > 0 and len(self.password) > 0:
            login_response = self.submit()
            if not login_response:
                data = "There was a network error, please check your connection and try again."
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2), self.gEngine.SCREEN_HEIGHT / 2 - 3,
                                 1, 5, "Alert")
                pop.setup(data)
                self.gEngine.add_module(pop)
            else:
                data = login_response['message']
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2),
                                 self.gEngine.SCREEN_HEIGHT / 2 - 3, 1, 5, "Alert")
                pop.setup(data)
                if login_response['data']['player_id'] > 0:
                    self.close()
                    self.gEngine.player_id = login_response['data']['player_id']
                self.gEngine.add_module(pop)

        elif len(self.user_name) == 0 and len(self.password) == 0:
            data = "You must enter a username and password to login or create a new account!"
            pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2), self.gEngine.SCREEN_HEIGHT / 2 - 3, 1,
                             5, "Alert")
            pop.setup(data)
            self.gEngine.add_module(pop)

        elif len(self.user_name) == 0:
            data = "Username cannot be empty!"
            pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2), self.gEngine.SCREEN_HEIGHT / 2 - 3, 1,
                             5, "Alert")
            pop.setup(data)
            self.gEngine.add_module(pop)

        elif len(self.password) == 0:
            data = "Password cannot be empty!"
            pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2 - (len(data) / 2), self.gEngine.SCREEN_HEIGHT / 2 - 3, 1,
                             5, "Alert")
            pop.setup(data)
            self.gEngine.add_module(pop)

    def submit(self):
        request_type = "add_player"
        data = {'user_name': self.user_name, 'user_pass': self.password}
        response = self.gEngine.network_send_package(request_type, data)
        if response:
            return response
        return False
