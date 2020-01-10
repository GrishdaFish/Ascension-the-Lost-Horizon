__author__ = 'GrishdaFish'
import math
from gEngine.utilities.user_interface import menu
import tcod as libtcod


class DungeonStatus:
    def __init__(self, gEngine, game, x=0, y=0, w=0, h=5, title="", target_console=0):
        self.active = True
        self.game = game
        self.gEngine = gEngine
        self.x = x
        self.y = y
        self.width = self.gEngine.SCREEN_WIDTH / 2
        self.height = 5
        self.original_width = self.width
        self.original_height = self.height
        self.title = title
        self.is_dragging = False
        self.in_drag_zone = False
        self.con = self.gEngine.console_new(self.width, self.height)
        self.minimized = False
        self.target_console = target_console
        self.collapsed = False
        self.original_title = title
        self.collapse_button = '-'
        self.minimize_button = 'x'

    def set_title(self, title):
        self.title = title

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.deactivate()
        self.gEngine.console_remove_console(self.con)

    def update(self, key, mouse):
        pass

    def run(self, key, mouse):
        self.basic_mouse_input(mouse)
        self.pre_draw_widgit()
        self.update(key, mouse)
        self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, self.x, self.y, 1.0, 1.0)

    def mouse_is_in_console(self, mouse):
        if mouse.cx >= self.x and mouse.cx <= self.x + self.width:
            if mouse.cy >= self.y and mouse.cy <= self.y + self.height:
                return True
        return False

    def basic_mouse_input(self, mouse):
        if self.mouse_is_in_console(mouse):
            mousex = math.ceil(mouse.cx - self.x)
            mousey = math.ceil(mouse.cy - self.y)
            if mousex == self.width-1 and mousey == 0:
                self.minimize_button = menu.color_text(self.minimize_button, libtcod.green)
                if mouse.lbutton:
                    self.minimize()

            elif mousex == 0 and mousey == 0:
                self.collapse_button = menu.color_text(self.collapse_button, libtcod.green)
                if mouse.lbutton:
                    self.collapse()

            # else:
            #     self.minimize_button = menu.color_text(self.minimize_button, libtcod.white)
            #     self.collapse_button = menu.color_text(self.collapse_button, libtcod.white)

    def pre_draw_widgit(self):
        self.gEngine.console_print_frame(self.con, 0, 0, self.width, self.height, True)
        self.gEngine.console_print(self.con, self.width / 2 - (len(self.title) / 2), 0, self.title)
        self.gEngine.console_print(self.con, 0, 0, '-')
        self.gEngine.console_print(self.con, self.width-1, 0, 'x')

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

    def minimize(self):
        if self.minimized:
            self.minimized = False
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