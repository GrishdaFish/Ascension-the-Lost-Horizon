__author__ = 'GrishdaFish'

import math
from gEngine.utilities.user_interface import window_widget
from gEngine.utilities.user_interface import menu

import tcod as libtcod

class LoginPopup(window_widget.WindowWidget):
    def close(self):
        self.gEngine.remove_module(self)

    def setup(self, message):
        self.message = message
        self.width = len(message) + 2
        self.original_width = self.width
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)

    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        # notify user of something like bad password, no user name/pass, etc.. Just a confirm widget
        if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_ESCAPE or key.vk == libtcod.KEY_SPACE:
            self.close()
        self.gEngine.console_print(self.con, 1, 1, self.message)
        data = "Ok"
        if self.mouse_is_in_console(mouse):
            if mousex == 1 and mousex > self.width - 1:
                if mousey == 2:
                    # highlight "ok" button
                    data = menu.color_text(data, libtcod.green)
                    if mouse.lbutton:
                        self.close()
        data = menu.color_text(data, color_b=libtcod.grey)
        self.gEngine.console_print(self.con, self.width/2 - 1, 2, data)


class LoginMenu(window_widget.WindowWidget):
    def setup(self):
        self.user_text = "Username:"
        self.pass_text = "Password:"
        self.user_name = ''
        self.password = ''
        self.in_user = False
        self.in_pass = False
        self.frame_blink = 0
        self.is_blinking = True
        self.carrot = "|"

    def toggle_carrot(self):
        if self.is_blinking:
            self.carrot = ' '
        else:
            self.carrot = "|"
        self.is_blinking = not self.is_blinking

    def handle_keys(self, key):
        if key.c:
            if len(self.user_name) > 24:
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2, self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                pop.setup("Username cannot be more than 25 characters long")
                self.gEngine.add_module(pop)
            elif len(self.password) > 24:
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2, self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                pop.setup("Password cannot be more than 25 characters long")
                self.gEngine.add_module(pop)
            elif self.in_user:
                self.user_name += chr(key.c)
            elif self.in_pass:
                self.password += chr(key.c)

        if key.vk == libtcod.KEY_BACKSPACE:
            if self.in_user:
                if len(self.user_name) > 0:
                    list(self.user_name).pop(len(self.user_name) - 1)

            if self.in_pass:
                if len(self.password) > 0:
                    list(self.password).pop(len(self.password) - 1)

        if key.vk == libtcod.KEY_TAB:
            if self.in_user:
                self.in_user = False
                self.in_pass = True
            elif self.in_pass:
                pass  # do we try to submit or jump back to user?

        if key.vk == libtcod.KEY_ENTER:
            if len(self.user_name) > 0 and len(self.password) > 0:
                success = self.submit()
                if not success:
                    pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2, self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                    pop.setup("SUBMIT FAIL MESSAGE")
                    self.gEngine.add_module(pop)
                else:
                    pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2,
                                     self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                    pop.setup("You are now logged in...")
                    self.gEngine.add_module(pop)
            elif len(self.user_name) == 0 and len(self.password) == 0:
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2, self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                pop.setup("You must enter a username and password to login or create a new account!")
                self.gEngine.add_module(pop)
            elif len(self.user_name) == 0:
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2, self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                pop.setup("Username cannot be empty!")
                self.gEngine.add_module(pop)
            elif len(self.password) == 0:
                pop = LoginPopup(self.gEngine, self.game, self.gEngine.SCREEN_WIDTH / 2, self.gEngine.SCREEN_HEIGHT / 2, 1, 5, "Alert")
                pop.setup("Password cannot be empty!")
                self.gEngine.add_module(pop)

    def update(self, key, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        self.gEngine.console_print(self.con, 1, 1, "Login")
        use_data = self.user_text + " "
        pass_data = self.pass_text + " "
        if self.mouse_is_in_console(mouse):
            if mousex >= 1 and mousex < self.width - 1:
                if mousey == 2:
                    use_data = menu.color_text(use_data, libtcod.green)
                    if mouse.lbutton:
                        self.in_user = True
                        self.in_pass = False
                elif mousey == 3:
                    pass_data = menu.color_text(pass_data, libtcod.green)
                    if mouse.lbutton:
                        self.in_pass = True
                        self.in_user = False

        self.handle_keys(key)
        use_data += self.user_name
        pass_data += self.password
        self.gEngine.console_print(self.con, 1, 2, use_data)
        if self.in_user:
            self.gEngine.console_print(self.con, (len(self.user_text) + len(self.user_name)+2), 2, self.carrot)

        self.gEngine.console_print(self.con, 1, 3, pass_data)
        if self.in_pass:
            self.gEngine.console_print(self.con, (len(self.pass_text) + len(self.password)+2), 3, self.carrot)

        if self.frame_blink < 9:
            self.frame_blink += 1
        else:
            self.frame_blink = 0
            self.toggle_carrot()

    def submit(self):
        request_type = "add_player"
        data = {'user_name': self.user_name, 'user_pass': self.password}
        logged_in = self.gEngine.network_send_package(request_type, data)
        return logged_in