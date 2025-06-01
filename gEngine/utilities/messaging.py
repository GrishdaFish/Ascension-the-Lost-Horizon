import textwrap
import tcod as libtcod
import traceback


class Message:
    def __init__(self, message_console, MESSAGE_SCREEN_HEIGHT, MESSAGE_SCREEN_WIDTH, MSG_X, gEngine, x_pos=0, y_pos=0, debug='debug'):
        self.message_list = []
        self.message_log = []
        self.message_console = message_console
        self.MESSAGE_SCREEN_HEIGHT = MESSAGE_SCREEN_HEIGHT
        self.MESSAGE_SCREEN_WIDTH = MESSAGE_SCREEN_WIDTH# - MSG_X
        self.MSG_X = MSG_X
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.gEngine = gEngine
        self.debug_level = debug

    def message(self, message="", code=4):
        # Add support for custom colored strings (code 0)
        # NOTE, CANNOT PARSE A COLOR VALUE OF 0 (ZERO) WITH STRING FORMATTING. SET TO 1 OR 256!!
        # Color Coding for messages
        r, g, b = 0, 0, 0
        colors = {1: (100, 100, 100),  # grey
                  2: (255, 1, 1),  # red
                  3: (255, 255, 1),  # yellow
                  4: (255, 255, 255),  # white
                  5: (255, 127, 1),  # orange
                  }

        #self.gEngine.log_message(message, 'debug')
        msg = textwrap.wrap(message, self.MESSAGE_SCREEN_WIDTH-1)
        if isinstance(code, libtcod.Color):
            r, g, b = code
        else:
            if code > len(colors):
                code = 4
                r, g, b = colors[code]
            elif code == 0:  # arranging the message, with custom color coding
                for mes in msg:
                    self.message_log.append(mes)
                    self.message_list.append(mes)
                    while len(self.message_list) >= self.MESSAGE_SCREEN_HEIGHT - 1:
                        self.message_list.pop(0)
                return
            else:
                r, g, b = colors[code]
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
        while len(self.message_list) >= self.MESSAGE_SCREEN_HEIGHT - 1:
            self.message_list.pop(0)

    def flush_messages(self):
        # This is old code, will update later. This is based on how Ascension's UI is set up

        self.gEngine.console_set_alignment(self.message_console, libtcod.LEFT)
        self.gEngine.console_print_frame(self.message_console, 0, 0, self.MESSAGE_SCREEN_WIDTH, self.MESSAGE_SCREEN_HEIGHT+1, False)
        self.gEngine.console_print_frame(self.message_console, self.MSG_X-1, 0, self.MESSAGE_SCREEN_WIDTH -21,
                                        self.MESSAGE_SCREEN_HEIGHT +1, False)
        self.gEngine.console_print(self.message_console, self.MSG_X - 1, 0, chr(libtcod.CHAR_TEES))
        self.gEngine.console_print(self.message_console, self.MSG_X - 1, self.MESSAGE_SCREEN_HEIGHT, chr(libtcod.CHAR_TEEN))
        for i in range(len(self.message_list)):
            self.gEngine.console_print(self.message_console, self.MSG_X, 1 + i, self.message_list[i])

    def render(self):
        self.gEngine.console_blit(self.message_console, 0, 0, self.MESSAGE_SCREEN_WIDTH, self.MESSAGE_SCREEN_HEIGHT, 0, self.x_pos, self.y_pos, 1.0, 1.0)
        #self.gEngine.console_clear(self.message_console)

    def error_message(self, err, game):
        self.gEngine.log_message(err, 'error')
        i = 4
        msg = ''
        if self.debug_level == 'debug':
            mes = traceback.format_exc(err)
            mes = textwrap.wrap(mes, 50)
            i = 2
            for m in mes:
                msg += m + '\n'
                i += 1
        elif self.debug_level == 'release':
            msg = 'Error! Details in debug/error.txt. Please submit a bug report.'
        confirm = 'Press any key to continue.'
        #menu.confirm_screen(0, msg, 50, 80, confirm, height=i, game=game)
