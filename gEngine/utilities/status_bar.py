import tcod as libtcod


class StatusBar:
    def __init__(self, size, full, empty, con, gEngine=None):
        self.bar = gEngine.image_new(size * 2, 2)
        self.full = full
        self.empty = empty
        self.size = size * 2
        self.con = con

    def render(self, px, py, gEngine, values=None, name=None):
        if values:
            value = values[0]
            maximum = values[1]
            msg = name.capitalize() + ': ' + str(value) + '/' + str(int(maximum))
        else:
            gEngine.log_open_block("No  values passed to status bar.render()")
            gEngine.log_close_block()
            return

        if value <= 0:
            bar = int(float(self.size) / (maximum / 0.1))
        else:
            bar = int(float(self.size) / (float(maximum) / float(value)))

        if bar > self.size:
            bar = self.size
        r, g, b = self.empty
        gEngine.image_clear(self.bar, r, g, b)
        r, g, b = self.full
        for i in range(bar):
            gEngine.image_put_pixel(self.bar, i, 0, r, g, b)
            gEngine.image_put_pixel(self.bar, i, 1, r, g, b)

        gEngine.image_blit_2x(self.bar, self.con, px, py)
        r, g, b = libtcod.white
        gEngine.console_set_default_foreground(self.con, r, g, b)
        gEngine.console_print(self.con, px, py, msg)

    def remove_bar(self, bars):
        pass

    def hover_description(self):
        names = [self.type.capitalize()]
        if 'hp':
            names.append(str(self.owner.hp) + " / " + str(self.owner.stat.get_stat_base("HP")))
            names.append("Regen rate: " + str(self.owner.stat.get_stat("Regen")))
        if 'mp':
            pass
        if 'xp':
            pass
        if 'torch':
            pass


class AnimatedStatusBar:
    def __init__(self, background, foreground, animation, target_console, gEngine, x, y):
        self.x = x
        self.y = y
        self.background = gEngine.image_load(background)
        self.foreground = gEngine.image_load(foreground)
        self.animation = animation
        self.target_console = target_console
        self.gEngine = gEngine
        w, h = gEngine.image_get_size(self.foreground)
        print(w, h)
        self.fore_con = gEngine.console_new(w / 2, h / 2)
        self.size = w
        w, h = gEngine.image_get_size(self.background)
        print(w, h)
        self.back_con = gEngine.console_new(w / 2, h / 2)

    def update(self, values):
        value = values[0]
        maximum = values[1]
        animation_off = False
        if maximum <= 0:
            maximum = 0.1
        if value <= 0:
            animation_off = True
            length = int(float(self.size) / (maximum / 0.1))
        else:
            animation_off = False
            length = int(float(self.size) / (float(maximum) / float(value)))
        if length > self.size:
            length = self.size
        self.gEngine.console_print(self.back_con, 0, 0, "Test")
        self.gEngine.image_blit_2x(self.background, self.back_con, 0, 0)
        self.gEngine.image_blit_2x(self.foreground, self.fore_con, 0, 0)
        if not animation_off:
            self.gEngine.animation_draw_animation(self.animation, self.back_con, self.x + length / 2 - 2, self.y - 3)

        self.gEngine.console_blit(self.back_con, 0, 0, 0, 0, self.target_console, self.x, self.y, 1.0, 1.0)
        if not animation_off:
            self.gEngine.console_blit(self.fore_con, 0, 0, length / 2, 0, self.target_console, self.x, self.y, 1.0, 1.0)

    def render(self):
        pass