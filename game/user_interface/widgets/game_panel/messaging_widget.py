__author__ = 'GrishdaFish'
from game.user_interface.widgets.game_panel import *
import textwrap
import tcod as libtcod

class MessagingPanel(panels.StaticPanel):
    def __init__(self, gEngine, parent, x=0, y=0, w=0, h=0, title="Messages", draw_frame=True)->None:
        super().__init__(gEngine, parent, x, y, w, h, title, draw_frame)
        self.message_list = []
        self.message_log = []
        self.color_codes = {1: (100, 100, 100),  # grey
                            2: (255, 1, 1),  # red
                            3: (255, 255, 1),  # yellow
                            4: (255, 255, 255),  # white
                            5: (255, 127, 1),  # orange
                            }
    def message(self, message: str="", code: int=4)->None:
        msg = textwrap.wrap(message, self.w-1)
        if isinstance(code, libtcod.Color):
            r, g, b = code
        else:
            if code > len(self.color_codes):
                code = 4
                r, g, b = self.color_codes[code]
            elif code == 0:  # arranging the message, with custom color coding
                for mes in msg:
                    self.message_log.append(mes)
                    self.message_list.append(mes)
                    while len(self.message_list) >= self.h - 1:
                        self.message_list.pop(0)
                return
            else:
                r, g, b = self.color_codes[code]
        if r == 0:
            r = 1
        if g == 0:
            g = 1
        if b == 0:
            b = 1
        for mes in msg:
            mes = ("%c%c%c%c%s%c " % (libtcod.COLCTRL_FORE_RGB, r, g, b, mes, libtcod.COLCTRL_STOP))
            self.message_list.append(mes)
            self.message_log.append(mes)

        # TODO add in message history for session
        # If there are more messages than room to display them, drop the top one to give the scrolling effect
        while len(self.message_list) >= self.h- 1:
            self.message_list.pop(0)

    def flush_messages(self)->None:
        self.gEngine.console_set_alignment(self.con, libtcod.LEFT)

        for i in range(len(self.message_list)):
            self.gEngine.console_print(self.con, 1, 1 + i, self.message_list[i])
    def update(self, key, mouse)->None:
        self.flush_messages()