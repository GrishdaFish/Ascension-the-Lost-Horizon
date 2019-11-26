import tcod as libtcod
from gEngine.utilities.user_interface import menu


class Tab:
    def __init__(self, dest_x=0, dest_y=0, parent=None, label=None, x_pos=None,
                 y_pos=None, game=None, window=None, onclick=None):
        """
        :param dest_x:
        :param dest_y:
        :param parent: The object this tab is attached to
        :param label: The label of the tab
        :param x_pos: The position this tab is located, relative to parent if one, or game screen otherwise
        :param y_pos: Same as above
        :param game: The main game instance
        :param window: Destination window if there is no parent
        :param onclick: Function to trigger when this tab is clicked
        """
        self.width = 4 + len(label)
        self.height = 3
        self.on_click = onclick
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
            self.dest_window = window
            self.dest_x = self.parent.x_pos
            self.dest_y = self.parent.y_pos
        self.window = self.parent.game.gEngine.console_new(self.width, self.height)
        self.label = label
        self.label_o = label
        r, g, b = libtcod.white
        self.parent.game.gEngine.console_set_default_foreground(self.window, r, g, b)
        self.parent.game.gEngine.console_set_alignment(self.window, 2)

    def display(self, mouse=None):
        """
        :param mouse: libtcod.Mouse() instance
        """
        self.parent.game.gEngine.console_blit(self.window, 0, 0, self.width, self.height, self.dest_window, self.x_pos,
                                              self.y_pos, 1.0, 1.0)
        self.parent.game.gEngine.console_print_frame(self.window, 0, 0, self.width, self.height, False)
        self.parent.game.gEngine.console_print(self.window, self.width / 2, self.height / 2, self.label)
        self.mouse_input(mouse)

    def destroy_tab(self):
        self.parent.game.gEngine.console_remove_console(self.window)

    def mouse_input(self, mouse=None):
        key = libtcod.Key()
        if not mouse:
            mouse = libtcod.mouse_get_status()
        libtcod.sys_check_for_event(libtcod.EVENT_MOUSE, key, mouse)
        mx = mouse.cx - (self.x_pos + self.dest_x)
        my = mouse.cy - (self.y_pos + self.dest_y)

        if 0 <= mx <= self.width and 0 <= my <= self.height:
            self.label = menu.color_text(self.label_o, libtcod.red)
            if mouse.lbutton:
                down = True
                while down:
                    self.label = menu.color_text(self.label_o, libtcod.green)
                    if mouse.lbutton_pressed:
                        self.on_click()
                        return
                    mouse = libtcod.Mouse()
                    libtcod.sys_check_for_event(libtcod.EVENT_MOUSE, key, mouse)
                    if not mouse.lbutton:
                        down = False
        else:
            self.label = menu.color_text(self.label_o, libtcod.white)

        return
