__author__ = 'GrishdaFish'
import math
from gEngine.utilities.user_interface import menu
import tcod as libtcod

# TODO Figure out how widgets are automatically getting added to gEngine module list??????
class WindowWidget:
    def __init__(self, gEngine, game=None, x=0, y=0, w=0, h=5, title="", target_console=0):
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
        #self.gEngine.remove_module(self)

    def update(self, key, mouse):
        pass

    def run(self, key, mouse):
        if self.active:
            self.gEngine.console_clear(self.con)
        else:
            return
        self.basic_mouse_input(mouse)
        self.pre_draw_widgit()
        if self.check_for_overlap():
            mouse = libtcod.Mouse()
            key = libtcod.Key()
        self.update(key, mouse)
        if self.active:
            self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, self.x, self.y, 1.0, 1.0)

    def mouse_is_in_console(self, mouse):
        if self.x <= mouse.cx <= self.x + math.floor(self.width):
            if self.y <= mouse.cy <= self.y + math.floor(self.height):
                return True
        return False

    def check_for_overlap(self):
        module = self.get_overlap_module()
        if module:
            if self.gEngine.modules.index(self) > self.gEngine.modules.index(module):
                return False
            else:
                return True
        return False

    def get_overlap_module(self):
        for module in self.gEngine.modules:
            if isinstance(module, WindowWidget):
                if module != self:
                    if module.active:
                        if (self.x <= module.x + math.floor(module.width) and
                                self.x + math.floor(self.width) >= module.x and
                                self.y <= module.y + math.floor(module.height) and
                                self.y + math.floor(self.height) >= module.y):
                            return module
        return None

    def in_overlap_zone(self, mouse):
        other_module = self.get_overlap_module()
        if other_module:
            left_overlap = max(self.x, other_module.x)
            right_overlap = min(self.x + self.width, other_module.x + other_module.width) - 1
            top_overlap = max(self.y, other_module.y)
            bottom_overlap = min(self.y + self.height, other_module.y + other_module.height) - 1
            if mouse.cx >= left_overlap and mouse.cx <= right_overlap:
                if mouse.cy >= top_overlap and mouse.cy <= bottom_overlap:
                    return other_module
        else:
            return None

    def basic_mouse_input(self, mouse):
        mousex = math.ceil(mouse.cx - self.x)
        mousey = math.ceil(mouse.cy - self.y)
        if self.mouse_is_in_console(mouse):
            if mouse.lbutton:
                other_module = self.in_overlap_zone(mouse)
                if other_module:
                    if self.gEngine.modules.index(self) > self.gEngine.modules.index(other_module):
                        pass
                elif self.gEngine.modules.index(self) < len(self.gEngine.modules) - 1:
                    self.gEngine.bring_module_to_front(self)
        if self.is_dragging:
            self.x = mouse.cx - self.dragx
            self.y = mouse.cy - self.dragy
        if not self.check_for_overlap():
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

            if mousex == self.width - 1 and mousey == 0 and not self.is_dragging:
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
            #libtcod
            #self.gEngine.console_set_default_Foreground(self.con,)
            self.gEngine.console_print_frame(self.con, 0, 0, self.width, self.height, True)
            self.gEngine.console_print(self.con, self.title_x_position, 0, self.title)
            self.gEngine.console_print(self.con, 0, 0, self.collapse_button)
            self.gEngine.console_print(self.con, self.width - 1, 0, self.minimize_button)

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
        self.on_exit()

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
