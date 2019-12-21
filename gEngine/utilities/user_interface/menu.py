import tcod as libtcod



def color_text(text, color_f=None, color_b=None):
    # changed to not use color codes, as the items were all colored the same
    # this gives the intended effect
    # txt = text.capitalize()
    txt = text
    rf, gf, bf, rb, gb, bb = 1, 1, 1, 1, 1, 1

    if color_f:
        rf, gf, bf = color_f
        # make sure none of the rgb vlaues are 0
        if rf == 0: rf = 1
        if gf == 0: gf = 1
        if bf == 0: bf = 1
    if color_b:
        rb, gb, bb = color_b
        # make sure none of the rgb vlaues are 0
        if rb == 0: rb = 1
        if gb == 0: gb = 1
        if bb == 0: bb = 1
    # if text is colored and we just need background changed (highlighting)
    # Cant just change the background color here. not working for some stupid reason
    if not color_f and color_b:
        return '%c%c%c%c%s%c' % (libtcod.COLCTRL_BACK_RGB, rb, gb, bb, txt, libtcod.COLCTRL_STOP)
    if color_f and not color_b:
        return '%c%c%c%c%s%c' % (libtcod.COLCTRL_FORE_RGB, rf, gf, bf, txt, libtcod.COLCTRL_STOP)
    if color_f and color_b:
        return "%c%c%c%c%c%c%c%c%s%c" % (libtcod.COLCTRL_FORE_RGB, rf, gf, bf,
                                         libtcod.COLCTRL_BACK_RGB, rb, gb, bb, txt, libtcod.COLCTRL_STOP)


class Menus:
    def __init__(self, gEngine, screen_height, screen_width, width, header, options,
                 con=None, bg=None, cl_options=None):
        self.is_dragging = False
        self.in_drag_zone = False
        self.mouse_highlight = False
        self.gEngine = gEngine
        self.cl_options = cl_options
        self.img = None
        if bg:
            self.img = self.gEngine.image_load(bg)

        self.screen_height = screen_height
        self.screen_width = screen_width

        self.header = header
        # if len(self.header) == 0:
        #    self.header = '======='
        self.header_o = self.header

        self.options = options

        height = len(options)
        width += 5
        height += 2
        # self.header_pos = (width//2)-len(header)

        self.window = self.gEngine.console_new(width, height)
        self.gEngine.console_set_alignment(self.window, 2)

        self.width = width
        self.height = height
        self.w_pos = screen_width / 2 - width / 2
        self.h_pos = screen_height / 2 - height / 2

        self.dragx = None
        self.dragy = None

        self.is_visible = False
        self.can_drag = True

        self.last_input = 0
        libtcod.mouse_get_status()  # this is to pick up stray mouse input that
        # shouldnt be picked up.

    def run(self):
        if self.is_visible:
            y = 0
            letter_index = ord('a')
            r, g, b = libtcod.white

            # if self.img:
            #     self.gEngine.image_blit_2x(self.img, 0, 0, 0)
            self.gEngine.console_set_alignment(self.window, libtcod.LEFT)
            self.gEngine.console_set_default_foreground(self.window, r, g, b)
            self.gEngine.console_blit(self.window, 0, 0, self.width,
                                      self.height, 0, self.w_pos, self.h_pos, 1.0, 1.0)

            self.gEngine.console_print_frame(self.window, 0, 0,
                                             self.width, self.height, False)

            if self.can_drag:
                self.gEngine.console_print(self.window, self.width / 2, 0, self.header)

            self.gEngine.console_print(self.window, 0, 0, chr(254))
            self.gEngine.console_print(self.window, self.width - 1, 0, chr(158))

            for i in range(len(self.options)):
                text = '(' + chr(letter_index) + ') ' + self.options[i]
                self.gEngine.console_print(self.window, 1, y + 1, text)
                y += 1
                letter_index += 1

            self.gEngine.console_flush()
            m_input = self.mouse_input()
            k_input = self.key_input()
            if m_input != -1:
                if m_input == 'close':
                    return None
                else:
                    return m_input

            if k_input != -1:
                if k_input == 'close':
                    return None
                else:
                    return k_input

            return -1

    def destroy_menu(self):
        if self.img:
            self.gEngine.image_delete(self.img)
        self.gEngine.console_remove_console(self.window)

    def mouse_input(self):
        # Menu Mouse Input
        mouse_choice = None
        mouse = libtcod.Mouse()
        key, mouse = self.gEngine.handle_input(mouse=mouse)#libtcod.mouse_get_status()
        #print(mouse.cx, mouse.cy)
        mx = mouse.cx - self.w_pos
        my = mouse.cy - self.h_pos

        # for dragging
        if 2 <= mx <= self.width - 2 and my == 0:
            self.in_drag_zone = True
            if not self.is_dragging:
                self.header = color_text(self.header_o, libtcod.red)
        else:
            if not self.is_dragging:
                self.header = color_text(self.header_o, libtcod.white)
                self.in_drag_zone = False

        if mouse.lbutton and not self.is_dragging and self.in_drag_zone:
            self.is_dragging = True
            self.header = color_text(self.header_o, libtcod.green)
            self.dragx = mx
            self.dragy = my

        elif not mouse.lbutton and self.is_dragging:
            self.is_dragging = False

        elif self.is_dragging and self.can_drag:
            self.w_pos = mouse.cx - self.dragx
            self.h_pos = mouse.cy - self.dragy

        # For Close button
        if mouse.cx == self.w_pos + self.width - 1 and mouse.cy == self.h_pos and not self.is_dragging:
            t = color_text('X', libtcod.red)
            self.gEngine.console_print(self.window, self.width - 1, 0, t)
            if mouse.lbutton_pressed:
                libtcod.mouse_get_status()
                return 'close'

        # For Menu Options
        letter_index = ord('a')
        if self.w_pos <= mouse.cx <= self.w_pos + self.width and not self.is_dragging:
            for i in range(len(self.options)):
                if my == i + 1:
                    if self.cl_options is not None:
                        t = '(' + chr(letter_index + i) + ') ' + self.cl_options[i].capitalize()
                    else:
                        t = '(' + chr(letter_index + i) + ') ' + self.options[i].capitalize()
                    text = color_text(t, color_f=libtcod.red)
                    self.gEngine.console_print(self.window, 1, i + 1, text)
                    self.mouse_highlight = True
                    mouse_choice = i
                    break
                else:
                    self.mouse_highlight = False

        # bug here, after selecting a choice, the next menu gets "clicked" as well.
        # FIXED. Just called mouse_get_status() on __init__ and before a return
        # to pick up unwanted input
        if mouse.lbutton and self.mouse_highlight and not self.is_dragging:
            if not mouse.lbutton:
                libtcod.mouse_get_status()
            return mouse_choice
        return -1

    def key_input(self):
        # Menu Keyboard Input
        key, mouse = self.gEngine.handle_input()# libtcod.console_check_for_keypress()

        index = key.c - ord('a')

        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if key.vk == libtcod.KEY_ESCAPE:
            libtcod.console_check_for_keypress()
            return 'close'

        if key:
            if 0 <= index < len(self.options):
                libtcod.console_check_for_keypress()
                return index

        # if key.vk == libtcod.KEY_DOWN:
        #    current_pick = (current_pick +1) % len(self.options)

        # if key.vk == libtcod.KEY_UP:
        #    current_pick = (current_pick -1) % len(self.options)

        # if key.vk == libtcod.KEY_ENTER:
        #    return current_pick

        return -1


def menu(con, header, options, width, SCREEN_HEIGHT, SCREEN_WIDTH, bg=None, game=None, under=None):
    ##for menus that dont need to have positions tracked
    if len(options) > 26:
        if game:
            game.logger.error('Cannot have a menu with more than 26 options.')
        raise ValueError('Cannot have a menu with more than 26 options.')

    if header == '':
        header = '======='
    if bg:
        img = game.gEngine.image_load(bg)
        game.gEngine.image_blit_2x(img, 0, 0, 0)

    height = len(options)
    width += 5
    height += 2
    header_pos = (width // 2) - len(header)

    window = game.gEngine.console_new(width, height)

    current_pick = 0
    y = 0
    letter_index = ord('a')
    w_pos = SCREEN_WIDTH / 2 - width / 2
    h_pos = SCREEN_HEIGHT / 2 - height / 2

    r, g, b = libtcod.white
    game.gEngine.console_set_default_foreground(window, r, g, b)
    original_header = header
    is_dragging = False
    in_drag_zone = False
    mouse_highlight = False
    mouse = None
    key = libtcod.console_check_for_keypress()
    first_run = True

    while key.vk is not libtcod.KEY_NONE:
        key = libtcod.console_check_for_keypress(True)

    while not libtcod.console_is_window_closed():
        game.gEngine.console_flush()
        game.gEngine.console_blit(window, 0, 0, width, height, 0, w_pos, h_pos, 1.0, 1.0)

        game.gEngine.console_clear(window)

        game.gEngine.console_print_frame(window, 0, 0, width, height, False)

        game.gEngine.console_print(window, header_pos, 0, header)
        game.gEngine.console_print(window, 0, 0, chr(254))
        game.gEngine.console_print(window, width - 1, 0, chr(158))

        for i in range(len(options)):
            text = '(' + chr(letter_index) + ') ' + options[i]
            game.gEngine.console_print(window, 1, y + 1, text)
            y += 1
            letter_index += 1
        y = 0
        letter_index = ord('a')

        ##Menu Mouse Input
        mouse = libtcod.mouse_get_status()
        mx = mouse.cx - w_pos
        my = mouse.cy - h_pos

        ##for dragging
        if w_pos + header_pos <= mouse.cx <= w_pos + header_pos + len(original_header) - 1 and mouse.cy == h_pos:
            in_drag_zone = True
            if not is_dragging:
                header = color_text(original_header, libtcod.red)
        else:
            header = color_text(original_header, libtcod.white)
            in_drag_zone = False

        if mouse.lbutton and not is_dragging and in_drag_zone:
            is_dragging = True
            header = color_text(original_header, libtcod.green)
            dragx = mx
            dragy = my

        elif not mouse.lbutton and is_dragging:
            is_dragging = False

        elif is_dragging:
            w_pos = mouse.cx - dragx
            h_pos = mouse.cy - dragy

        ##For Close button
        if mouse.cx == w_pos + width - 1 and mouse.cy == h_pos:
            t = color_text('X', libtcod.red)
            game.gEngine.console_print(window, width - 1, 0, t)
            if mouse.lbutton_pressed:
                if bg:
                    game.gEngine.image_delete(img)
                libtcod.mouse_get_status()
                return None

        ##For Menu Options
        if w_pos <= mouse.cx <= w_pos + width:
            for i in range(len(options)):
                if my == i + 1:
                    t = '(' + chr(letter_index + i) + ') ' + options[i].capitalize()
                    text = color_text(t, color_f=libtcod.red)
                    game.gEngine.console_print(window, 1, i + 1, text)
                    mouse_highlight = True
                    mouse_choice = i
                    break
                else:
                    mouse_highlight = False

        ##bug here, after selecting a choice, the next menu gets "clicked" as well.
        ##if set to lbutton, only the last option in a list seems to work
        if mouse.lbutton and mouse_highlight:
            if bg:
                game.gEngine.image_delete(img)
            libtcod.mouse_get_status()
            return mouse_choice

        ##Menu Keyboard Input
        key = libtcod.console_check_for_keypress(True)

        index = key.c - ord('a')

        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if key.vk == libtcod.KEY_ESCAPE:
            game.gEngine.console_remove_console(window)
            if bg:
                game.gEngine.image_delete(img)
            libtcod.console_check_for_keypress()
            return None

        if key:
            if index >= 0 and index < len(options):
                game.gEngine.console_remove_console(window)
                if bg:
                    game.gEngine.image_delete(img)
                libtcod.console_check_for_keypress()
                return index

        if key.vk == libtcod.KEY_DOWN:
            current_pick = (current_pick + 1) % len(options)

        if key.vk == libtcod.KEY_UP:
            current_pick = (current_pick - 1) % len(options)

        if key.vk == libtcod.KEY_ENTER:
            game.gEngine.console_remove_console(window)
            if bg:
                game.gEngine.image_delete(img)
            libtcod.console_check_for_keypress()
            return current_pick

        first_run = False


def msgbox(text, width=50, con=None, SCREEN_HEIGHT=50, SCREEN_WIDTH=80):
    menu(con, text, [], width, SCREEN_HEIGHT, SCREEN_WIDTH)  # use menu() as a sort of "message box"


def confirm_screen(con, message, screen_height, screen_width,
                   confirm_key_message='Press [y] or [Enter] to confirm.',
                   confirm_keys=[ord('y'), libtcod.KEY_ENTER], height=4, game=None):
    if len(message) > len(confirm_key_message):
        width = len(message) + 2
    else:
        width = len(confirm_key_message) + 2
    height = height
    window = game.gEngine.console_new(width, height)

    r, g, b = libtcod.white
    game.gEngine.console_set_default_foreground(window, r, g, b)
    game.gEngine.console_print_frame(window, 0, 0, width, height, True)
    game.gEngine.console_set_alignment(window, libtcod.CENTER)
    game.gEngine.console_print(window, width / 2, 1, message)

    game.gEngine.console_print(window, width / 2, height - 1, confirm_key_message)

    x = screen_width / 2 - width / 2
    y = screen_height / 2 - height / 4
    game.gEngine.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
    game.gEngine.console_flush()

    key = libtcod.console_wait_for_keypress(True)
    if key.c in confirm_keys or key.vk in confirm_keys:
        game.gEngine.console_remove_console(window)
        return True
    else:
        game.gEngine.console_remove_console(window)
        return False
