import math
from gEngine import lights
import tcod as libtcod

from gEngine.utilities.user_interface.menu import color_text


def select_ammo(ox, oy, dx, dy, shooter, game, target=None):
    ammo_types = []
    weapon_type = shooter.fighter.gear.get_quipped_weapon_type()
    for item in shooter.fighter.inventory:
        # TODO do we need to check stackable and stack items here?
        if item.equipment.subtype == weapon_type and item.equipment.type == "ammo":
            ammo_types.append(item)
    if ammo_types:
        return Popup(game.gEngine, game.dungeon_console, ammo_types, dx, dy)
    else:
        print("You gots none ammo's noob!")
        return None

def fire_shot(ox, oy, dx, dy, shooter, game, target=None):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))

    ddx = math.cos(angle * 1.0)
    ddy = math.sin(angle * 1.0)

    final_x = ox + ddx * 1.0
    final_y = oy + ddy * 1.0

    i = libtcod.random_get_float(0, 1.0, 1.15)
    l = lights.Light(int(final_x), int(final_y), game.light_handler, 1.0, 0.05, i)
    game.light_handler.add_light(l)
    if target:
        if shooter == game.player:
            shooter.fighter.attack(target, player=True, game=game)
        else:
            shooter.fighter.attack(target, player=False, game=game)
    else:
        blind_fire(dx, dy, ox, oy, game, shooter)



def blind_fire(dx, dy, ox, oy, game, shooter):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))

    ddx = math.cos(angle * 1.0)
    ddy = math.sin(angle * 1.0)
    final_x = ox + ddx
    final_y = oy + ddy
    target = None
    while True:
        target = game.check_for_target(int(final_x), int(final_y))
        if target:
            break
        if game.level.dungeon[int(final_x)][int(final_y)].blocked:
            game.message.message('hit wall')
            i = libtcod.random_get_float(0, 0.65, 0.85)
            l = lights.Light(int(final_x - ddx), int(final_y - ddy), game.light_handler, 2.0, 0.05, i)
            game.light_handler.add_light(l)
            break
        final_x += ddx * 1.0
        final_y += ddy * 1.0

    if target:
        if shooter == game.player:
            shooter.fighter.attack(target, player=True, game=game)
        else:
            shooter.fighter.attack(target, player=False, game=game)


class Popup:
    def __init__(self, gEngine, target, data, x, y):  # target = game.dungeon_console
        self.gEngine = gEngine
        self.target_console = target
        self.width = 0
        self.height = 0
        self.title = None
        self.populate(data)
        self.x = x
        self.y = y
        self.console = self.gEngine.console_new(self.width, self.height)

    def mouse_is_in_console(self, mouse):
        if mouse.cx > self.x and mouse.cx < self.x + self.width:
            if mouse.cy > self.y and mouse.cy < self.y + self.height:
                return True
        return False

    def update(self, mouse):
        r, g, b = libtcod.black
        self.gEngine.console_set_default_background(self.console, r, g, b)
        self.gEngine.console_print_frame(self.console, 0, 0, self.width, self.height, True, self.title)
        mouse_index = None
        if self.mouse_is_in_console(mouse):
            cx = mouse.cx - self.x
            cy = mouse.cy - self.y
            mouse_index = cy
        i = 1
        selected = None
        for line in self.data:
            if mouse_index == i:
                line = color_text(line, libtcod.red)
                selected = self.data[i - 1]
            else:
                line = color_text(line, libtcod.white)
            self.gEngine.console_print(self.console, 1, i, line)
            i += 1
        if mouse.lbutton and selected:
            return mouse_index - 1
        else:
            return None

    def render(self, game):
        self.gEngine.console_blit(self.console, self.target, 0, 0, self.width, self.height, self.x, self.y)

    def populate(self, data):
        self.data = data
        self.width = self.get_longest_line() + 2  # addtional width for frame
        self.title = self.data.pop(0)
        self.height = len(self.data) + 2  # addition height for frame

    def get_longest_line(self):
        longest_line_length = 0
        for line in self.data:
            if len(line) > longest_line_length:
                longest_line_length = len(line)
        return longest_line_length