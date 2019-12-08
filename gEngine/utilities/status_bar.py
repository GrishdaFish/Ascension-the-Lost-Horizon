import tcod as libtcod


class StatusBar:
    def __init__(self, owner, size, full, empty, con, type='hp', gEngine=None):
        self.bar = gEngine.image_new(size * 2, 2)
        self.full = full
        self.empty = empty
        self.owner = owner
        self.size = size * 2
        self.con = con
        self.type = type

    def render(self, px, py, gEngine=None):
        maximum, value = 0, 0
        if self.type == 'hp':
            value = int(self.owner.hp)
            maximum = int(self.owner.stat.get_stat_by_name("HP"))
        if self.type == 'mp':
            pass
        if self.type == 'xp':
            value = self.owner.current_xp
            maximum = int(self.owner.get_xp_tnl())
        if self.type == 'status':  # for status ailments or buffs like poison, stun or regen
            pass

        if self.type == 'torch':
            if self.owner.light_source:
                self.full = self.owner.light_source.item.equipment.torch_color
                value = int(self.owner.light_source.item.equipment.fuel)
                maximum = int(self.owner.light_source.item.equipment.max_fuel)
            else:
                self.full = self.empty
                value = 0
                maximum = 0

        if maximum <= 0:
            maximum = 0.1

        msg = self.type.capitalize() + ': ' + str(value) + '/' + str(int(maximum))

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
        gEngine.console_set_alignment(self.con, int(libtcod.CENTER))
        gEngine.console_print(self.con, px + self.size / 4, py, msg)

    def remove_bar(self, bars):
        pass
