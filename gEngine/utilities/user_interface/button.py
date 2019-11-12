import tcod as libtcod
from gEngine.utilities.user_interface import menu

class Button:
    def __init__(self, dest_x=0, dest_y=0, parent=None, label=None, x_pos=None,
                 y_pos=None, type=True, game=None, window=None):
        self.width = 4 + len(label)
        self.height = 5
        self.x_pos = x_pos
        self.y_pos = y_pos
        if parent is None:
            self.game = game
            self.parent = self
            self.dest_window = window
            self.dest_x = dest_x
            self.dest_y = dest_y
        else:
            self.parent = parent
            self.dest_window = self.parent.window
            self.dest_x = self.parent.x_pos
            self.dest_y = self.parent.y_pos
        self.window = self.parent.game.gEngine.console_new(self.width, self.height)
        self.label = label
        self.label_o = label
        r, g, b = libtcod.white
        self.parent.game.gEngine.console_set_default_foreground(self.window, r, g, b)
        self.parent.game.gEngine.console_set_alignment(self.window, 2)
        self.type = type

    def display(self, mouse=None):
        self.parent.game.gEngine.console_blit(self.window, 0, 0, self.width,
                                              self.height, self.dest_window, self.x_pos, self.y_pos, 1.0, 1.0)

        self.parent.game.gEngine.console_print_frame(self.window, 0, 0,
                                                     self.width, self.height, False)

        self.parent.game.gEngine.console_print(self.window, self.width / 2,
                                               self.height / 2, self.label)
        #self.parent.game.gEngine.console_flush()

        k = self.key_input()
        m = self.mouse_input()
        if mouse:
            m = self.mouse_input(mouse)
        return m, k

    def destroy_button(self):
        self.parent.game.gEngine.console_remove_console(self.window)

    def mouse_input(self, mouse=None):
        key = libtcod.Key()
        if not mouse:
            mouse = libtcod.mouse_get_status()
        mx = mouse.cx - (self.x_pos + self.dest_x)
        my = mouse.cy - (self.y_pos + self.dest_y)

        if 0 <= mx <= self.width and 0 <= my <= self.height:
            self.label = menu.color_text(self.label_o, libtcod.red)
            if mouse.lbutton:
                down = True
                while down:
                    self.label = menu.color_text(self.label_o, libtcod.green)
                    if mouse.lbutton_pressed:
                        if self.type is True:
                            return 1
                        else:
                            return 0
                    mouse = libtcod.Mouse()
                    libtcod.sys_check_for_event(libtcod.EVENT_MOUSE, key, mouse)
                    if not mouse.lbutton:
                        down = False

            if mouse.lbutton_pressed:
                if self.type is True:
                    return 1
                else:
                    return 0
        else:
            self.label = menu.color_text(self.label_o, libtcod.white)

        return -1

    def key_input(self):
        key = libtcod.Key()
        mouse = libtcod.Mouse()
        libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)

        if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_SPACE:
            libtcod.console_check_for_keypress()
            return 1
        if key.vk == libtcod.KEY_ESCAPE:
            libtcod.console_check_for_keypress()
            return 0
        return -1
