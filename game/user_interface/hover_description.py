__author__ = 'GrishdaFish'
from game import render
import tcod as libtcod

class HoverDescription:
    def __init__(self, target_console, gEngine, border=False):
        """
        To display any sort of information on top of any panel
        :param target_console: the panel to place this console over
        :param border: If you would like the console to have a border around it
        """
        self.border = border
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.content = []
        self.display_console = None
        self.target_console = target_console
        self.gEngine = gEngine

    def update(self, mouse, content, max_height):
        """
        updates this class with mouse position and the content to display to it
        :param max_height: the maximum height of the screen for clamping
        :param mouse: libtcod.Mouse() class, for positional requirements
        :param content: the content to be displayed on the panel. Requires a list of at least Len(1)
        :return: Nothing
        """
        if len(content) < 1:
            # why did you not give me content? Shame. :'(
            return
        if self.border:
            self.height += 2
            self.width += 2
        self.height += len(content)
        longest_line = 0
        for line in content:
            length = len(line)
            if length > longest_line:
                longest_line = length
        self.width += longest_line
        self.display_console = self.gEngine.console_new(self.width, self.height)

        self.x = mouse.cx
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > self.gEngine.w:
            self.x = self.gEngine.w - self.width
        self.y = mouse.cy
        if self.y <= 0:
            self.y = 1
        elif self.y + self.height > max_height:
            self.y = max_height - self.height

        self.content = content


    def render(self, game, inject=False):
        """
        Renders this console ontop of the target console, call this after you blit the target console
        but before you flush output
        :param inject: Do we use game/render.py render_all injection? use this if rendering to a main game console
        :return: an injected renderer list or None
        """
        if len(self.content) == 0:
            return None
        if self.display_console:
            if inject:
                return [self.injected_render]
                #render.render_all(game, renderer)
            else:
                r, g, b = libtcod.white
                game.gEngine.console_set_default_background(self.display_console, r, g, b)
                offset = 0
                if self.border:
                    game.gEngine.console_print_frame(self.display_console, 0, 0, self.width, self.height, True)
                    offset += 1
                if len(self.content) > 1:
                    for y in range(len(self.content) - 1):
                        game.gEngine.console_print(self.display_console, offset, y + offset, self.content[y])
                else:
                    game.gEngine.console_print(self.display_console, offset, 0 + offset, self.content[0])
                game.gEngine.console_blit(self.display_console, 0, 0, 0, 0, self.target_console,
                                          self.x, self.y - 1, 1.0, 1.0)
                return None

    def injected_render(self, game):
        """
        Used for injecting into render.render_all() to draw on the target console
        :param game:
        :return:
        """
        r, g, b = libtcod.white
        game.gEngine.console_set_default_background(self.display_console, r, g, b)
        offset = 0
        if self.border:
            game.gEngine.console_print_frame(self.display_console, 0, 0, self.width, self.height, True)
            offset += 1
        if len(self.content) > 1:
            for y in range(len(self.content)):
                game.gEngine.console_print(self.display_console, offset, y + offset, self.content[y])
        else:
            game.gEngine.console_print(self.display_console, offset, 0 + offset, self.content[0])
        game.gEngine.console_blit(self.display_console, 0, 0, 0, 0, self.target_console,
                                  self.x, self.y - 1, 1.0, 1.0)

    def reset(self):
        """
        Resets all data, including the console, so we arent always displaying a console if one doesnt exist
        :return:
        """
        self.display_console = None
        self.content = []
        self.width = 0
        self.height = 0