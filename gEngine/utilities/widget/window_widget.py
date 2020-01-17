__author__ = 'GrishdaFish'
import math
from gEngine.utilities.user_interface import menu
import tcod as libtcod


class WindowWidget:
    def __init__(self, gEngine, game, x=0, y=0, w=0, h=5, title="", target_console=0):
        """
        Basic widget for the engine. Inheret this class. Override update. Add to gEngine.modules
        All required functions are set up to work with nothing over-ridden. Only over-ride functions if you know what
        you're doing.
        :param gEngine: Active instance of gEngine
        :param game: Active Game instance
        :param x: The starting X position for the widget
        :param y: The Starting Y position for the widget
        :param w: The width of the widget
        :param h: The Height of the widget
        :param title: The title to be displayed
        :param target_console: Console to blit this on top of. Defaults to root
        """
        self.active = True
        self.game = game
        self.gEngine = gEngine
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.original_width = self.width
        self.original_height = self.height

        self.title = title
        self.original_title = title
        self.title_x_position = self.width / 2 - (len(self.title) / 2)

        self.is_dragging = False
        self.in_drag_zone = False
        self.dragx = None
        self.dragy = None

        self.con = self.gEngine.console_new(self.width, self.height)
        self.target_console = target_console

        self.minimized = False
        self.collapsed = False
        self.collapse_button = '-'
        self.minimize_button = 'x'

    def activate(self):
        self.active = True
        self.minimized = False
        self.collapsed = False
        self.gEngine.console_remove_console(self.con)
        self.width = self.original_width
        self.height = self.original_height
        self.title = self.original_title
        self.con = self.gEngine.console_new(self.width, self.height)

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.deactivate()
        self.gEngine.console_remove_console(self.con)

    def update(self, key, mouse):
        pass

    def run(self, key, mouse):
        if self.active:
            self.gEngine.console_clear(self.con)
        self.basic_mouse_input(mouse)
        self.pre_draw_widgit()
        self.update(key, mouse)
        if self.active:
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, self.x, self.y, 1.0, 1.0)

    def mouse_is_in_console(self, mouse):
        if self.x <= mouse.cx <= self.x + math.floor(self.width):
            if self.y <= mouse.cy <= self.y + math.floor(self.height):
                return True
        return False

    def basic_mouse_input(self, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)

        if 1 <= mousex <= self.width - 2 and mousey == 0:
            self.in_drag_zone = True
            if not self.is_dragging:
                self.title = menu.color_text(self.original_title, libtcod.red)
        else:
            if not self.is_dragging:
                self.title = menu.color_text(self.original_title, libtcod.white)
                self.in_drag_zone = False

        if mouse.lbutton and not self.is_dragging and self.in_drag_zone:
            self.is_dragging = True
            self.title = menu.color_text(self.original_title, libtcod.green)
            self.dragx = mousex  # mouse.cx  # - self.width/2
            self.dragy = mousey  # mouse.cy

        elif mouse.lbutton_pressed and self.is_dragging:
            self.is_dragging = False

        elif self.is_dragging:
            self.x = mouse.cx - self.dragx
            self.y = mouse.cy - self.dragy

        if mousex == self.width-1 and mousey == 0 and not self.is_dragging:
            self.minimize_button = menu.color_text('x', libtcod.green)
            if mouse.lbutton:
                self.minimize()

        elif mousex == 0 and mousey == 0 and not self.is_dragging:
            self.collapse_button = menu.color_text('-', libtcod.green)
            if mouse.lbutton:
                self.collapse()

        else:
            self.minimize_button = menu.color_text('x', libtcod.white)
            self.collapse_button = menu.color_text('-', libtcod.white)

    def pre_draw_widgit(self):
        if self.active:
            self.gEngine.console_print_frame(self.con, 0, 0, self.width, self.height, True)
            self.gEngine.console_print(self.con, self.title_x_position, 0, self.title)
            self.gEngine.console_print(self.con, 0, 0, self.collapse_button)
            self.gEngine.console_print(self.con, self.width-1, 0, self.minimize_button)

    def collapse(self):
        if self.collapsed:
            self.collapsed = False
            self.gEngine.console_remove_console(self.con)
            self.height = self.original_height
            self.con = self.gEngine.console_new(self.width, self.height)
        else:
            self.gEngine.console_remove_console(self.con)
            self.height = 1
            self.con = self.gEngine.console_new(self.width, self.height)
            self.collapsed = True

    def close(self):
        """
        Over-ride to change behavior of the 'x' button
        """
        self.gEngine.remove_module(self)

    def minimize(self):
        self.close()
        if self.minimized:
            self.minimized = False
            self.collapsed = False
            self.gEngine.console_remove_console(self.con)
            self.width = self.original_width
            self.height = self.original_height
            self.title = self.original_title
            self.con = self.gEngine.console_new(self.width, self.height)
        else:
            self.gEngine.console_remove_console(self.con)
            self.width = 3
            self.height = 2
            self.con = self.gEngine.console_new(self.width, self.height)
            self.minimized = True
            self.title = '='
